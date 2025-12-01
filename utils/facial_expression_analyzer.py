"""
FACIAL EXPRESSION ANALYZER
Detects whispering, reading, anxiety, suspicious behaviors
Using Action Units (AUs) approximation from landmarks
"""
import numpy as np
from collections import deque


class FacialExpressionAnalyzer:
    def __init__(self):
        # Expression history
        self.expression_history = deque(maxlen=90)  # 3 seconds
        
        # AU thresholds
        self.WHISPER_THRESHOLD = 0.6
        self.READING_THRESHOLD = 0.7
        self.ANXIETY_THRESHOLD = 0.65
        
    def calculate_mouth_aspect_ratio(self, landmarks):
        """Calculate mouth opening (AU25, AU26)"""
        if landmarks is None or len(landmarks) < 68:
            return 0
        
        # Mouth landmarks
        mouth_top = landmarks[51]
        mouth_bottom = landmarks[57]
        mouth_left = landmarks[48]
        mouth_right = landmarks[54]
        
        # Vertical distance
        vertical = np.linalg.norm(mouth_top - mouth_bottom)
        # Horizontal distance
        horizontal = np.linalg.norm(mouth_left - mouth_right)
        
        # Aspect ratio
        mar = vertical / (horizontal + 1e-6)
        
        return mar
    
    def calculate_eyebrow_raise(self, landmarks):
        """Calculate eyebrow raise (AU01, AU02)"""
        if landmarks is None or len(landmarks) < 68:
            return 0
        
        # Left eyebrow
        left_brow = landmarks[19]
        left_eye = landmarks[37]
        left_dist = np.linalg.norm(left_brow - left_eye)
        
        # Right eyebrow
        right_brow = landmarks[24]
        right_eye = landmarks[44]
        right_dist = np.linalg.norm(right_brow - right_eye)
        
        # Average distance (normalized)
        avg_dist = (left_dist + right_dist) / 2
        
        return avg_dist
    
    def calculate_eye_squint(self, landmarks):
        """Calculate eye squinting (AU07)"""
        if landmarks is None or len(landmarks) < 68:
            return 0
        
        # Left eye
        left_top = landmarks[37]
        left_bottom = landmarks[41]
        left_height = np.linalg.norm(left_top - left_bottom)
        
        # Right eye
        right_top = landmarks[43]
        right_bottom = landmarks[47]
        right_height = np.linalg.norm(right_top - right_bottom)
        
        # Average (smaller = more squint)
        avg_height = (left_height + right_height) / 2
        
        return avg_height
    
    def calculate_lip_corner_pull(self, landmarks):
        """Calculate lip corner pulling (AU12, AU14)"""
        if landmarks is None or len(landmarks) < 68:
            return 0
        
        # Lip corners
        left_corner = landmarks[48]
        right_corner = landmarks[54]
        mouth_center = landmarks[51]
        
        # Distance from corners to center
        left_dist = np.linalg.norm(left_corner - mouth_center)
        right_dist = np.linalg.norm(right_corner - mouth_center)
        
        # Average pull
        avg_pull = (left_dist + right_dist) / 2
        
        return avg_pull
    
    def calculate_chin_raise(self, landmarks):
        """Calculate chin raise (AU17)"""
        if landmarks is None or len(landmarks) < 68:
            return 0
        
        chin = landmarks[8]
        lower_lip = landmarks[57]
        
        dist = np.linalg.norm(chin - lower_lip)
        
        return dist
    
    def detect_whispering(self, landmarks, gaze_direction):
        """
        Detect whispering pattern
        AU25 + AU26 + gaze down = whispering
        """
        mar = self.calculate_mouth_aspect_ratio(landmarks)
        
        # Small mouth opening with movement
        is_whispering = (0.05 < mar < 0.15 and gaze_direction == "down")
        
        return is_whispering
    
    def detect_reading(self, landmarks, gaze_direction):
        """
        Detect reading from notes
        AU01 + AU02 + AU05 + AU45 spike + gaze down = reading
        """
        if gaze_direction != "down":
            return False
        
        brow_raise = self.calculate_eyebrow_raise(landmarks)
        mar = self.calculate_mouth_aspect_ratio(landmarks)
        
        # Concentrated reading expression
        is_reading = (brow_raise > 15 and mar < 0.1)
        
        return is_reading
    
    def detect_hiding_smile(self, landmarks):
        """
        Detect hiding a smile (someone helping)
        AU12 + AU14 abnormal = hiding smile
        """
        lip_pull = self.calculate_lip_corner_pull(landmarks)
        mar = self.calculate_mouth_aspect_ratio(landmarks)
        
        # Lip corners pulled but mouth not fully open
        is_hiding_smile = (lip_pull > 25 and mar < 0.2)
        
        return is_hiding_smile
    
    def detect_anxiety(self, landmarks, blink_rate):
        """
        Detect anxiety/stress
        AU04 + AU07 + high blink rate = anxiety
        """
        eye_squint = self.calculate_eye_squint(landmarks)
        
        # Squinting + high blink rate
        is_anxious = (eye_squint < 5 and blink_rate > 30)
        
        return is_anxious
    
    def detect_confusion(self, gaze_shifts):
        """
        Detect confusion (looking between two sources)
        Repeated gaze shifts = confusion/cheating
        """
        if len(gaze_shifts) < 10:
            return False
        
        # Count direction changes in last 10 frames
        changes = 0
        for i in range(1, len(gaze_shifts)):
            if gaze_shifts[i] != gaze_shifts[i-1]:
                changes += 1
        
        # More than 5 changes in 10 frames = suspicious
        is_confused = changes > 5
        
        return is_confused
    
    def analyze_expression(self, landmarks, gaze_direction, blink_rate, gaze_history):
        """
        Complete facial expression analysis
        Returns: dict with all detected behaviors
        """
        behaviors = {
            'whispering': False,
            'reading': False,
            'hiding_smile': False,
            'anxiety': False,
            'confusion': False,
            'suspicious_score': 0
        }
        
        if landmarks is None:
            return behaviors
        
        # Detect all behaviors
        behaviors['whispering'] = self.detect_whispering(landmarks, gaze_direction)
        behaviors['reading'] = self.detect_reading(landmarks, gaze_direction)
        behaviors['hiding_smile'] = self.detect_hiding_smile(landmarks)
        behaviors['anxiety'] = self.detect_anxiety(landmarks, blink_rate)
        
        # Detect confusion from gaze history
        recent_gaze = list(gaze_history)[-10:] if len(gaze_history) >= 10 else []
        behaviors['confusion'] = self.detect_confusion(recent_gaze)
        
        # Calculate suspicious score
        score = 0
        if behaviors['whispering']:
            score += 30
        if behaviors['reading']:
            score += 40
        if behaviors['hiding_smile']:
            score += 20
        if behaviors['anxiety']:
            score += 10
        if behaviors['confusion']:
            score += 25
        
        behaviors['suspicious_score'] = min(100, score)
        
        return behaviors
