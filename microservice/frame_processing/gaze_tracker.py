"""
Gaze Tracking Module
Estimates gaze direction from iris position
"""
import cv2
import numpy as np
from typing import Dict, Tuple, Optional


class GazeTracker:
    """Gaze tracking using iris detection"""
    
    def __init__(self):
        self.LEFT_EYE = list(range(36, 42))
        self.RIGHT_EYE = list(range(42, 48))
        self.threshold_x = 3
        self.threshold_y = 3
    
    async def load_models(self):
        """Load gaze tracking models (if any)"""
        pass  # Using iris-based detection, no models needed
    
    def estimate_gaze(self, frame: np.ndarray, landmarks: np.ndarray) -> Dict:
        """
        Estimate gaze direction
        
        Args:
            frame: BGR image
            landmarks: Facial landmarks (68, 2)
        
        Returns:
            Dictionary with gaze information
        """
        # Get eye regions
        left_iris = self._get_iris_center(frame, landmarks, self.LEFT_EYE)
        right_iris = self._get_iris_center(frame, landmarks, self.RIGHT_EYE)
        
        if left_iris is None and right_iris is None:
            return {'direction': 'unknown', 'gaze_x': 0, 'gaze_y': 0}
        
        # Calculate gaze vector
        gaze_x, gaze_y = 0, 0
        count = 0
        
        if left_iris is not None:
            left_center = np.mean(landmarks[self.LEFT_EYE], axis=0)
            gaze_x += left_iris[0] - left_center[0]
            gaze_y += left_iris[1] - left_center[1]
            count += 1
        
        if right_iris is not None:
            right_center = np.mean(landmarks[self.RIGHT_EYE], axis=0)
            gaze_x += right_iris[0] - right_center[0]
            gaze_y += right_iris[1] - right_center[1]
            count += 1
        
        if count > 0:
            gaze_x /= count
            gaze_y /= count
        
        # Classify direction
        direction = self._classify_direction(gaze_x, gaze_y)
        
        return {
            'direction': direction,
            'gaze_x': float(gaze_x),
            'gaze_y': float(gaze_y)
        }
    
    def _get_iris_center(self, frame: np.ndarray, landmarks: np.ndarray, eye_points: list) -> Optional[Tuple[float, float]]:
        """Extract iris center from eye region"""
        points = landmarks[eye_points]
        x, y, w, h = cv2.boundingRect(points.astype(np.int32))
        
        # Add padding
        padding = 5
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(frame.shape[1] - x, w + 2 * padding)
        h = min(frame.shape[0] - y, h + 2 * padding)
        
        eye_region = frame[y:y+h, x:x+w]
        
        if eye_region.size == 0:
            return None
        
        # Convert to grayscale and find darkest region (iris)
        gray = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        _, threshold = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return None
        
        # Get largest contour
        contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(contour)
        
        if M["m00"] == 0:
            return None
        
        cx = x + int(M["m10"] / M["m00"])
        cy = y + int(M["m01"] / M["m00"])
        
        return (cx, cy)
    
    def _classify_direction(self, gaze_x: float, gaze_y: float) -> str:
        """Classify gaze direction"""
        if abs(gaze_y) > self.threshold_y and gaze_y > 0:
            return "looking_down"
        elif abs(gaze_y) > self.threshold_y and gaze_y < 0:
            return "looking_up"
        elif abs(gaze_x) > self.threshold_x and gaze_x > 0:
            return "looking_right"
        elif abs(gaze_x) > self.threshold_x and gaze_x < 0:
            return "looking_left"
        else:
            return "looking_center"
