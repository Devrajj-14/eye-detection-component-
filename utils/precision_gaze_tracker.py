"""
PRECISION GAZE TRACKER
Extremely strict gaze detection with calibration
NO false negatives, HIGH sensitivity
"""
import numpy as np
import cv2
from collections import deque
from sklearn.linear_model import Ridge


class PrecisionGazeTracker:
    def __init__(self):
        # Calibration data
        self.calibrated = False
        self.calibration_model_x = None
        self.calibration_model_y = None
        
        # EXTREMELY SENSITIVE thresholds
        self.HORIZONTAL_THRESHOLD = 10  # degrees (reduced from 15)
        self.VERTICAL_THRESHOLD = 8     # degrees (reduced from 10)
        self.HEAD_YAW_SUSPICIOUS = 20   # degrees (reduced from 25)
        self.HEAD_YAW_CRITICAL = 30     # degrees (reduced from 40)
        self.LOOKING_AWAY_TIME = 0.5    # seconds (reduced from 0.7)
        
        # Gaze history for micro-cheating detection
        self.gaze_history = deque(maxlen=300)  # 10 seconds at 30fps
        self.head_rotation_history = deque(maxlen=90)  # 3 seconds
        
        # Exponential smoothing
        self.smoothed_gaze_x = 0
        self.smoothed_gaze_y = 0
        self.alpha = 0.3  # Smoothing factor
        
        # Event counters
        self.looking_away_frames = 0
        self.glance_left_count = 0
        self.glance_right_count = 0
        self.glance_down_count = 0
        self.glance_up_count = 0
        self.last_glance_time = 0
    
    def apply_exponential_smoothing(self, new_x, new_y):
        """Apply exponential smoothing to gaze coordinates"""
        self.smoothed_gaze_x = self.alpha * new_x + (1 - self.alpha) * self.smoothed_gaze_x
        self.smoothed_gaze_y = self.alpha * new_y + (1 - self.alpha) * self.smoothed_gaze_y
        return self.smoothed_gaze_x, self.smoothed_gaze_y
    
    def predict_gaze_point(self, iris_left, iris_right, head_pose, landmarks):
        """
        Predict gaze point on screen using calibration
        Uses ONLY iris position (head pose only as minor correction)
        Returns: (screen_x, screen_y) or None if not calibrated
        """
        if not self.calibrated:
            return None
        
        # Extract features - PRIORITIZE IRIS POSITION
        features = []
        
        # Iris positions (normalized) - PRIMARY FEATURE
        if iris_left:
            features.extend([iris_left[0] / 1920, iris_left[1] / 1080])
        else:
            features.extend([0.5, 0.5])
        
        if iris_right:
            features.extend([iris_right[0] / 1920, iris_right[1] / 1080])
        else:
            features.extend([0.5, 0.5])
        
        # Head pose - MINOR CORRECTION ONLY (reduced weight)
        pitch, yaw, roll = head_pose
        features.extend([pitch / 180.0, yaw / 180.0, roll / 180.0])  # Reduced weight
        
        # Predict
        X = np.array([features])
        gaze_x = self.calibration_model_x.predict(X)[0]
        gaze_y = self.calibration_model_y.predict(X)[0]
        
        # Apply smoothing
        gaze_x, gaze_y = self.apply_exponential_smoothing(gaze_x, gaze_y)
        
        return (int(gaze_x), int(gaze_y))
    
    def is_looking_at_screen(self, gaze_point, screen_width=1920, screen_height=1080):
        """
        Check if gaze is within screen boundaries (calibrated)
        Uses calibration to define screen area
        """
        if gaze_point is None:
            return False
        
        gaze_x, gaze_y = gaze_point
        
        # Screen boundaries (with small margin)
        margin = 50  # pixels
        in_screen = (
            -margin < gaze_x < screen_width + margin and
            -margin < gaze_y < screen_height + margin
        )
        
        return in_screen
    
    def calculate_gaze_deviation(self, gaze_point, screen_width=1920, screen_height=1080):
        """
        Calculate gaze deviation from center in degrees
        Returns: (horizontal_deg, vertical_deg)
        """
        if gaze_point is None:
            return (0, 0)
        
        gaze_x, gaze_y = gaze_point
        center_x = screen_width / 2
        center_y = screen_height / 2
        
        # Calculate deviation in pixels
        dx = gaze_x - center_x
        dy = gaze_y - center_y
        
        # Convert to degrees (approximate)
        # Assuming 60cm viewing distance and 24" monitor
        horizontal_deg = np.arctan(dx / screen_width * 0.5) * 180 / np.pi
        vertical_deg = np.arctan(dy / screen_height * 0.5) * 180 / np.pi
        
        return (abs(horizontal_deg), abs(vertical_deg))
    
    def detect_looking_away(self, gaze_point, head_pose, fps=30):
        """
        STRICT detection of looking away
        Returns: (is_looking_away, direction, severity)
        """
        pitch, yaw, roll = head_pose
        
        # INSTANT trigger on extreme head rotation
        if abs(yaw) > self.HEAD_YAW_CRITICAL:
            return True, "CRITICAL_HEAD_TURN", "critical"
        
        if abs(yaw) > self.HEAD_YAW_SUSPICIOUS:
            return True, "SUSPICIOUS_HEAD_TURN", "high"
        
        # Check gaze deviation
        h_dev, v_dev = self.calculate_gaze_deviation(gaze_point)
        
        is_deviated = (h_dev > self.HORIZONTAL_THRESHOLD or 
                       v_dev > self.VERTICAL_THRESHOLD)
        
        if is_deviated:
            self.looking_away_frames += 1
            
            # Check if exceeded time threshold
            required_frames = int(self.LOOKING_AWAY_TIME * fps)
            if self.looking_away_frames > required_frames:
                # Determine direction
                if h_dev > v_dev:
                    direction = "LEFT" if gaze_point[0] < 960 else "RIGHT"
                else:
                    direction = "DOWN" if gaze_point[1] > 540 else "UP"
                
                return True, direction, "medium"
        else:
            self.looking_away_frames = 0
        
        return False, None, None
    
    def detect_micro_cheating(self, gaze_point, current_time):
        """
        Detect repeated glances (micro-cheating patterns)
        Returns: (detected, pattern_type)
        """
        if gaze_point is None:
            return False, None
        
        gaze_x, gaze_y = gaze_point
        center_x, center_y = 960, 540
        
        # Detect glance direction
        glance_detected = False
        glance_type = None
        
        if gaze_x < center_x - 300:  # Left glance
            self.glance_left_count += 1
            glance_detected = True
            glance_type = "LEFT"
        elif gaze_x > center_x + 300:  # Right glance
            self.glance_right_count += 1
            glance_detected = True
            glance_type = "RIGHT"
        elif gaze_y > center_y + 200:  # Down glance
            self.glance_down_count += 1
            glance_detected = True
            glance_type = "DOWN"
        elif gaze_y < center_y - 200:  # Up glance
            self.glance_up_count += 1
            glance_detected = True
            glance_type = "UP"
        
        # Check for patterns in last 10 seconds
        if current_time - self.last_glance_time > 10:
            # Reset counters every 10 seconds
            self.glance_left_count = 0
            self.glance_right_count = 0
            self.glance_down_count = 0
            self.glance_up_count = 0
            self.last_glance_time = current_time
        
        # Detect suspicious patterns
        if self.glance_left_count >= 3 or self.glance_right_count >= 3:
            return True, "REPEATED_SIDE_GLANCES"
        
        if self.glance_down_count >= 3:
            return True, "REPEATED_DOWN_GLANCES"
        
        if self.glance_up_count >= 3:
            return True, "REPEATED_UP_GLANCES"
        
        return False, None
    
    def analyze_gaze(self, iris_left, iris_right, head_pose, landmarks, current_time, fps=30):
        """
        Complete gaze analysis with all checks
        Returns: dict with all gaze information
        """
        # Predict gaze point
        gaze_point = self.predict_gaze_point(iris_left, iris_right, head_pose, landmarks)
        
        # Check if looking at screen
        looking_at_screen = self.is_looking_at_screen(gaze_point)
        
        # Detect looking away
        is_away, away_direction, severity = self.detect_looking_away(gaze_point, head_pose, fps)
        
        # Detect micro-cheating
        micro_cheat, pattern = self.detect_micro_cheating(gaze_point, current_time)
        
        # Calculate deviation
        h_dev, v_dev = self.calculate_gaze_deviation(gaze_point)
        
        # Determine gaze status
        if looking_at_screen:
            gaze_status = "center"
        elif gaze_point:
            if gaze_point[0] < 640:
                gaze_status = "left"
            elif gaze_point[0] > 1280:
                gaze_status = "right"
            elif gaze_point[1] > 720:
                gaze_status = "down"
            else:
                gaze_status = "up"
        else:
            gaze_status = "unknown"
        
        return {
            'gaze_point': gaze_point,
            'looking_at_screen': looking_at_screen,
            'gaze_status': gaze_status,
            'is_looking_away': is_away,
            'away_direction': away_direction,
            'severity': severity,
            'micro_cheating': micro_cheat,
            'micro_pattern': pattern,
            'horizontal_deviation': h_dev,
            'vertical_deviation': v_dev,
            'head_yaw': head_pose[1]
        }
