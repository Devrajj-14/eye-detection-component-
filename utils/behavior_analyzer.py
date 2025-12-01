"""
Behavior Analysis Module
Analyzes facial expressions, stress levels, and suspicious behaviors
"""
import numpy as np
import cv2
from collections import deque


class BehaviorAnalyzer:
    def __init__(self):
        self.blink_history = deque(maxlen=100)
        self.expression_history = deque(maxlen=50)
        self.stress_indicators = []
        
        # Eye aspect ratio for blink detection
        self.EAR_THRESHOLD = 0.25
        self.BLINK_FRAMES = 3
        self.blink_counter = 0
        self.total_blinks = 0
        
    def calculate_eye_aspect_ratio(self, eye_landmarks):
        """Calculate Eye Aspect Ratio for blink detection"""
        if eye_landmarks is None or len(eye_landmarks) < 6:
            return 0.3
        
        # Vertical distances
        A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        
        # Horizontal distance
        C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        # EAR formula
        ear = (A + B) / (2.0 * C)
        return ear
    
    def detect_blink(self, landmarks):
        """Detect eye blinks"""
        if landmarks is None:
            return False
        
        # Left eye landmarks (36-41)
        left_eye = landmarks[36:42]
        # Right eye landmarks (42-47)
        right_eye = landmarks[42:48]
        
        left_ear = self.calculate_eye_aspect_ratio(left_eye)
        right_ear = self.calculate_eye_aspect_ratio(right_eye)
        
        ear = (left_ear + right_ear) / 2.0
        self.blink_history.append(ear)
        
        # Detect blink
        if ear < self.EAR_THRESHOLD:
            self.blink_counter += 1
        else:
            if self.blink_counter >= self.BLINK_FRAMES:
                self.total_blinks += 1
                self.blink_counter = 0
                return True
            self.blink_counter = 0
        
        return False
    
    def analyze_stress_level(self, landmarks, head_pose):
        """Analyze stress indicators from facial features"""
        if landmarks is None:
            return 0
        
        stress_score = 0
        
        # Rapid blinking (stress indicator)
        if len(self.blink_history) > 30:
            recent_blinks = sum(1 for ear in list(self.blink_history)[-30:] if ear < self.EAR_THRESHOLD)
            if recent_blinks > 15:  # More than 50% closed
                stress_score += 20
        
        # Head movement instability
        pitch, yaw, roll = head_pose
        if abs(pitch) > 15 or abs(yaw) > 15:
            stress_score += 10
        
        # Mouth tension (distance between lips)
        upper_lip = landmarks[51]
        lower_lip = landmarks[57]
        lip_distance = np.linalg.norm(upper_lip - lower_lip)
        
        if lip_distance < 5:  # Tight lips
            stress_score += 15
        
        return min(stress_score, 100)
    
    def detect_whispering(self, landmarks):
        """Detect potential whispering from lip movement"""
        if landmarks is None:
            return False
        
        # Mouth landmarks
        mouth_top = landmarks[51]
        mouth_bottom = landmarks[57]
        mouth_left = landmarks[48]
        mouth_right = landmarks[54]
        
        # Calculate mouth opening
        vertical_dist = np.linalg.norm(mouth_top - mouth_bottom)
        horizontal_dist = np.linalg.norm(mouth_left - mouth_right)
        
        # Small mouth opening with movement suggests whispering
        if 2 < vertical_dist < 8 and horizontal_dist > 20:
            return True
        
        return False
    
    def detect_reading_pattern(self, gaze_history):
        """Detect reading pattern from gaze movements"""
        if len(gaze_history) < 10:
            return False
        
        # Convert to list for slicing
        recent_gaze = list(gaze_history)[-10:]
        
        # Check for left-right scanning pattern
        left_count = sum(1 for g in recent_gaze if g == "looking_left")
        right_count = sum(1 for g in recent_gaze if g == "looking_right")
        
        # Alternating left-right suggests reading
        if left_count > 3 and right_count > 3:
            return True
        
        return False
    
    def calculate_attention_score(self, gaze_history):
        """Calculate attention score based on gaze consistency"""
        if len(gaze_history) < 30:
            return 100
        
        recent_gaze = list(gaze_history)[-30:]
        center_count = sum(1 for g in recent_gaze if g == "looking_center")
        
        attention_score = (center_count / len(recent_gaze)) * 100
        return attention_score
    
    def get_behavior_summary(self):
        """Get summary of behavior analysis"""
        return {
            'total_blinks': self.total_blinks,
            'avg_ear': np.mean(list(self.blink_history)) if self.blink_history else 0.3,
            'stress_indicators': len(self.stress_indicators)
        }
