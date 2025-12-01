"""
Behavior Analysis Module
Analyzes facial expressions and behavior patterns
"""
import numpy as np
from typing import Dict


class BehaviorAnalyzer:
    """Analyze behavior from facial landmarks"""
    
    def __init__(self):
        self.blink_threshold = 0.2
        self.mouth_threshold = 0.3
    
    def analyze(self, landmarks: np.ndarray, frame: np.ndarray) -> Dict:
        """
        Analyze behavior from landmarks
        
        Args:
            landmarks: Facial landmarks (68, 2)
            frame: BGR image
        
        Returns:
            Dictionary with behavior analysis
        """
        # Calculate eye aspect ratio (for blink detection)
        left_ear = self._eye_aspect_ratio(landmarks[36:42])
        right_ear = self._eye_aspect_ratio(landmarks[42:48])
        ear = (left_ear + right_ear) / 2.0
        
        # Calculate mouth aspect ratio (for whispering)
        mar = self._mouth_aspect_ratio(landmarks[48:68])
        
        # Detect whispering (small mouth opening)
        whispering = 0.1 < mar < 0.3
        
        # Estimate stress level (simplified)
        stress_level = self._estimate_stress(landmarks)
        
        # Detect reading pattern (would need temporal data)
        reading_pattern = False
        
        return {
            'whispering': whispering,
            'stress_level': stress_level,
            'reading_pattern': reading_pattern,
            'ear': ear,
            'mar': mar
        }
    
    def _eye_aspect_ratio(self, eye: np.ndarray) -> float:
        """Calculate eye aspect ratio"""
        # Vertical distances
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        
        # Horizontal distance
        C = np.linalg.norm(eye[0] - eye[3])
        
        # EAR
        ear = (A + B) / (2.0 * C)
        return ear
    
    def _mouth_aspect_ratio(self, mouth: np.ndarray) -> float:
        """Calculate mouth aspect ratio"""
        # Vertical distance
        A = np.linalg.norm(mouth[13] - mouth[19])
        B = np.linalg.norm(mouth[14] - mouth[18])
        C = np.linalg.norm(mouth[15] - mouth[17])
        
        # Horizontal distance
        D = np.linalg.norm(mouth[0] - mouth[6])
        
        # MAR
        mar = (A + B + C) / (3.0 * D)
        return mar
    
    def _estimate_stress(self, landmarks: np.ndarray) -> float:
        """Estimate stress level (simplified)"""
        # Calculate eyebrow position (higher = more stress)
        left_eyebrow = np.mean(landmarks[17:22], axis=0)
        right_eyebrow = np.mean(landmarks[22:27], axis=0)
        left_eye = np.mean(landmarks[36:42], axis=0)
        right_eye = np.mean(landmarks[42:48], axis=0)
        
        # Distance between eyebrow and eye
        left_dist = left_eyebrow[1] - left_eye[1]
        right_dist = right_eyebrow[1] - right_eye[1]
        
        # Normalize to 0-100 scale (simplified)
        avg_dist = (abs(left_dist) + abs(right_dist)) / 2
        stress = min(100, max(0, (20 - avg_dist) * 5))
        
        return stress
