"""
PRECISION ATTENTION CALCULATOR
Computes attention from gaze, head pose, eye openness, blink rate, facial tension
STRICT thresholds: <60% = WARNING, <40% = RISK, <30% = CRITICAL
"""
import numpy as np
from collections import deque


class PrecisionAttentionCalculator:
    def __init__(self):
        self.attention_history = deque(maxlen=90)  # 3 seconds
        self.blink_history = deque(maxlen=300)  # 10 seconds
        
        # Thresholds
        self.WARNING_THRESHOLD = 60
        self.RISK_THRESHOLD = 40
        self.CRITICAL_THRESHOLD = 30
        
    def calculate_gaze_attention(self, gaze_status):
        """
        Gaze contribution to attention
        center = 100%, away = 0%
        """
        if gaze_status == "center":
            return 100
        elif gaze_status in ["left", "right"]:
            return 30
        elif gaze_status == "down":
            return 10
        elif gaze_status == "up":
            return 20
        else:
            return 50  # Unknown
    
    def calculate_head_pose_attention(self, head_pose):
        """
        Head pose contribution to attention
        Straight = 100%, turned = lower
        """
        pitch, yaw, roll = head_pose
        
        # Calculate deviation from center
        deviation = abs(yaw) + abs(pitch) * 0.5
        
        # Convert to attention score
        if deviation < 10:
            return 100
        elif deviation < 20:
            return 80
        elif deviation < 30:
            return 50
        else:
            return 20
    
    def calculate_eye_openness_attention(self, eye_aspect_ratio):
        """
        Eye openness contribution
        Open eyes = attentive, closed = not attentive
        """
        if eye_aspect_ratio > 0.25:
            return 100
        elif eye_aspect_ratio > 0.20:
            return 80
        elif eye_aspect_ratio > 0.15:
            return 50
        else:
            return 20
    
    def calculate_blink_rate_attention(self, blink_rate):
        """
        Blink rate contribution
        Normal = attentive, too high/low = less attentive
        """
        # Normal blink rate: 15-20 per minute
        if 10 < blink_rate < 25:
            return 100
        elif 5 < blink_rate < 35:
            return 80
        else:
            return 60
    
    def calculate_facial_tension_attention(self, landmarks):
        """
        Facial tension indicates concentration
        """
        if landmarks is None:
            return 50
        
        # Calculate eyebrow position (concentration indicator)
        left_brow = landmarks[19]
        left_eye = landmarks[37]
        brow_dist = np.linalg.norm(left_brow - left_eye)
        
        # Higher brow = more concentrated
        if brow_dist > 15:
            return 100
        elif brow_dist > 12:
            return 80
        else:
            return 60
    
    def calculate_micromovement_attention(self, movement_score):
        """
        Micromovements indicate restlessness/distraction
        """
        # Lower movement = more attentive
        if movement_score < 5:
            return 100
        elif movement_score < 10:
            return 80
        elif movement_score < 20:
            return 60
        else:
            return 40
    
    def calculate_overall_attention(self, gaze_status, head_pose, eye_aspect_ratio, 
                                   blink_rate, landmarks, movement_score=5):
        """
        Calculate overall attention score (0-100)
        Weighted combination of all factors
        """
        # Calculate individual components
        gaze_att = self.calculate_gaze_attention(gaze_status)
        head_att = self.calculate_head_pose_attention(head_pose)
        eye_att = self.calculate_eye_openness_attention(eye_aspect_ratio)
        blink_att = self.calculate_blink_rate_attention(blink_rate)
        tension_att = self.calculate_facial_tension_attention(landmarks)
        movement_att = self.calculate_micromovement_attention(movement_score)
        
        # Weighted average
        weights = {
            'gaze': 0.35,
            'head': 0.25,
            'eye': 0.15,
            'blink': 0.10,
            'tension': 0.10,
            'movement': 0.05
        }
        
        attention = (
            gaze_att * weights['gaze'] +
            head_att * weights['head'] +
            eye_att * weights['eye'] +
            blink_att * weights['blink'] +
            tension_att * weights['tension'] +
            movement_att * weights['movement']
        )
        
        # Store in history
        self.attention_history.append(attention)
        
        return int(attention)
    
    def get_attention_status(self, attention_score):
        """
        Get attention status based on score
        """
        if attention_score >= self.WARNING_THRESHOLD:
            return "GOOD"
        elif attention_score >= self.RISK_THRESHOLD:
            return "WARNING"
        elif attention_score >= self.CRITICAL_THRESHOLD:
            return "RISK"
        else:
            return "CRITICAL"
    
    def check_sustained_low_attention(self, fps=30):
        """
        Check for sustained low attention
        Returns: (is_sustained, duration, severity)
        """
        if len(self.attention_history) < 60:  # Need at least 2 seconds
            return False, 0, None
        
        recent = list(self.attention_history)[-90:]  # Last 3 seconds
        
        # Check different thresholds
        below_60 = sum(1 for a in recent if a < 60)
        below_40 = sum(1 for a in recent if a < 40)
        below_30 = sum(1 for a in recent if a < 30)
        
        # Calculate duration
        duration = len(recent) / fps
        
        # Check conditions
        if below_30 > 0:
            return True, duration, "CRITICAL"
        elif below_40 > 60:  # More than 2 seconds
            return True, duration, "RISK"
        elif below_60 > 90:  # More than 3 seconds
            return True, duration, "WARNING"
        
        return False, 0, None
