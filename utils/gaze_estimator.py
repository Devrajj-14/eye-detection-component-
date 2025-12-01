"""
Eye gaze estimation using facial landmarks
"""
import cv2
import numpy as np


class GazeEstimator:
    def __init__(self):
        # Eye landmark indices (dlib 68-point model)
        self.LEFT_EYE = list(range(36, 42))
        self.RIGHT_EYE = list(range(42, 48))
        
        # Calibration data
        self.is_calibrated = False
        self.screen_bounds = None
        self.load_calibration()
    
    def get_eye_region(self, frame, landmarks, eye_points):
        """Extract eye region from frame"""
        if landmarks is None:
            return None, None
        
        points = landmarks[eye_points]
        x, y, w, h = cv2.boundingRect(points)
        
        # Add padding
        padding = 5
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(frame.shape[1] - x, w + 2 * padding)
        h = min(frame.shape[0] - y, h + 2 * padding)
        
        eye_region = frame[y:y+h, x:x+w]
        return eye_region, (x, y, w, h)
    
    def get_iris_center(self, eye_region):
        """Detect iris center in eye region"""
        if eye_region is None or eye_region.size == 0:
            return None
        
        gray = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY) if len(eye_region.shape) == 3 else eye_region
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        
        # Find darkest region (pupil/iris)
        _, threshold = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return None
        
        # Get largest contour
        contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(contour)
        
        if M["m00"] == 0:
            return None
        
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        
        return (cx, cy)
    
    def estimate_gaze(self, frame, landmarks, head_pose):
        """
        Estimate gaze direction using iris position + head pose
        Returns: (gaze_vector, direction_label, gaze_x, gaze_y)
        """
        if landmarks is None:
            return None, "unknown", 0, 0
        
        # Get left and right eye centers
        left_eye_region, left_box = self.get_eye_region(frame, landmarks, self.LEFT_EYE)
        right_eye_region, right_box = self.get_eye_region(frame, landmarks, self.RIGHT_EYE)
        
        left_iris = self.get_iris_center(left_eye_region) if left_eye_region is not None else None
        right_iris = self.get_iris_center(right_eye_region) if right_eye_region is not None else None
        
        # If no iris detected, use head pose only
        if left_iris is None and right_iris is None:
            pitch, yaw, roll = head_pose
            # Use head pose to determine direction
            if abs(yaw) > 15:
                direction = "looking_right" if yaw > 0 else "looking_left"
            elif abs(pitch) > 10:
                direction = "looking_down" if pitch > 0 else "looking_up"
            else:
                direction = "looking_center"
            
            nose_tip = tuple(landmarks[30])
            gaze_vector = (
                int(nose_tip[0] + yaw * 5),
                int(nose_tip[1] + pitch * 5)
            )
            return gaze_vector, direction, yaw, pitch
        
        # Calculate gaze vector from iris positions
        gaze_points = []
        
        if left_iris is not None and left_box is not None:
            lx, ly, lw, lh = left_box
            left_center = (lx + lw // 2, ly + lh // 2)
            left_iris_global = (lx + left_iris[0], ly + left_iris[1])
            gaze_points.append((left_iris_global, left_center))
        
        if right_iris is not None and right_box is not None:
            rx, ry, rw, rh = right_box
            right_center = (rx + rw // 2, ry + rh // 2)
            right_iris_global = (rx + right_iris[0], ry + right_iris[1])
            gaze_points.append((right_iris_global, right_center))
        
        # Average gaze vector
        gaze_x = 0
        gaze_y = 0
        
        for iris_pos, eye_center in gaze_points:
            gaze_x += iris_pos[0] - eye_center[0]
            gaze_y += iris_pos[1] - eye_center[1]
        
        gaze_x /= len(gaze_points)
        gaze_y /= len(gaze_points)
        
        # Check if gaze is within calibrated screen boundaries
        if self.is_calibrated:
            is_on_screen = self.is_gaze_on_screen(gaze_x, gaze_y)
            if is_on_screen:
                direction = "looking_center"  # Within screen = center
            else:
                direction = self.get_off_screen_direction(gaze_x, gaze_y)
        else:
            # Fallback: use simple classification
            direction = self._classify_direction(gaze_x, gaze_y)
        
        # Calculate gaze vector for visualization (using iris only)
        nose_tip = tuple(landmarks[30])
        gaze_vector = (
            int(nose_tip[0] + gaze_x * 10),
            int(nose_tip[1] + gaze_y * 10)
        )
        
        return gaze_vector, direction, gaze_x, gaze_y
    
    def _classify_direction(self, gaze_x, gaze_y):
        """
        Classify gaze direction from IRIS POSITION ONLY
        WITHOUT calibration - uses conservative thresholds
        """
        # Conservative thresholds for uncalibrated mode
        threshold_x = 3  # Moderate threshold
        threshold_y = 3  # Moderate threshold
        
        if abs(gaze_y) > threshold_y and gaze_y > 0:
            return "looking_down"
        elif abs(gaze_y) > threshold_y and gaze_y < 0:
            return "looking_up"
        elif abs(gaze_x) > threshold_x and gaze_x > 0:
            return "looking_right"
        elif abs(gaze_x) > threshold_x and gaze_x < 0:
            return "looking_left"
        else:
            return "looking_center"
    
    def load_calibration(self):
        """Load calibration data if available"""
        import os
        import json
        
        calibration_file = os.path.join('calibration', 'calibration_data.json')
        
        if os.path.exists(calibration_file):
            try:
                with open(calibration_file, 'r') as f:
                    data = json.load(f)
                
                self.screen_bounds = data['screen_bounds']
                self.is_calibrated = True
                print("✅ Calibration loaded successfully")
            except Exception as e:
                print(f"⚠️ Could not load calibration: {e}")
                self.is_calibrated = False
        else:
            print("ℹ️ No calibration found. Run calibrate_screen.py first.")
            self.is_calibrated = False
    
    def is_gaze_on_screen(self, gaze_x, gaze_y):
        """Check if gaze is within calibrated screen boundaries"""
        if not self.is_calibrated or self.screen_bounds is None:
            # Without calibration, use simple thresholds
            return abs(gaze_x) < 5 and abs(gaze_y) < 5
        
        # Use calibrated boundaries
        return (
            self.screen_bounds['gaze_x_min'] <= gaze_x <= self.screen_bounds['gaze_x_max'] and
            self.screen_bounds['gaze_y_min'] <= gaze_y <= self.screen_bounds['gaze_y_max']
        )
    
    def get_off_screen_direction(self, gaze_x, gaze_y):
        """Determine which direction eyes are looking off-screen"""
        if not self.is_calibrated or self.screen_bounds is None:
            # Fallback to simple classification
            if abs(gaze_x) > abs(gaze_y):
                return "LEFT_OF_SCREEN" if gaze_x < 0 else "RIGHT_OF_SCREEN"
            else:
                return "ABOVE_SCREEN" if gaze_y < 0 else "BELOW_SCREEN"
        
        # Use calibrated boundaries
        if gaze_x < self.screen_bounds['gaze_x_min']:
            return "LEFT_OF_SCREEN"
        elif gaze_x > self.screen_bounds['gaze_x_max']:
            return "RIGHT_OF_SCREEN"
        elif gaze_y < self.screen_bounds['gaze_y_min']:
            return "ABOVE_SCREEN"
        elif gaze_y > self.screen_bounds['gaze_y_max']:
            return "BELOW_SCREEN"
        else:
            return "ON_SCREEN"
    
    def draw_gaze(self, frame, landmarks, gaze_vector, direction):
        """Draw gaze vector and direction label"""
        if landmarks is None or gaze_vector is None:
            return
        
        nose_tip = tuple(landmarks[30])
        
        # Draw gaze line
        cv2.arrowedLine(frame, nose_tip, gaze_vector, (255, 0, 255), 2, tipLength=0.3)
        
        # Draw direction label
        label_pos = (nose_tip[0] + 10, nose_tip[1] - 10)
        cv2.putText(frame, direction, label_pos, 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
