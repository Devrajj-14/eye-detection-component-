"""
Calibration Module
Handles screen boundary calibration (optional feature)
"""
import numpy as np
from typing import Dict, List, Tuple


class Calibrator:
    """
    Screen boundary calibration
    Maps gaze coordinates to screen boundaries
    """
    
    def __init__(self):
        self.calibration_points = [
            (0.1, 0.1), (0.5, 0.1), (0.9, 0.1),
            (0.1, 0.5), (0.5, 0.5), (0.9, 0.5),
            (0.1, 0.9), (0.5, 0.9), (0.9, 0.9)
        ]
        self.calibration_data = []
        self.screen_bounds = None
    
    def add_calibration_sample(self, screen_point: Tuple[float, float], gaze_x: float, gaze_y: float) -> None:
        """Add a calibration sample"""
        self.calibration_data.append({
            'screen_point': screen_point,
            'gaze_x': gaze_x,
            'gaze_y': gaze_y
        })
    
    def compute_calibration(self, margin: float = 0.3) -> Dict:
        """
        Compute screen boundaries from calibration data
        
        Args:
            margin: Safety margin (0-1)
        
        Returns:
            Dictionary with screen bounds
        """
        if len(self.calibration_data) < 9:
            raise ValueError("Need at least 9 calibration samples")
        
        # Extract gaze values
        gaze_x_values = [s['gaze_x'] for s in self.calibration_data]
        gaze_y_values = [s['gaze_y'] for s in self.calibration_data]
        
        # Compute bounds with margin
        gaze_x_range = max(gaze_x_values) - min(gaze_x_values)
        gaze_y_range = max(gaze_y_values) - min(gaze_y_values)
        
        self.screen_bounds = {
            'gaze_x_min': min(gaze_x_values) - gaze_x_range * margin,
            'gaze_x_max': max(gaze_x_values) + gaze_x_range * margin,
            'gaze_y_min': min(gaze_y_values) - gaze_y_range * margin,
            'gaze_y_max': max(gaze_y_values) + gaze_y_range * margin,
        }
        
        return self.screen_bounds
    
    def is_within_bounds(self, gaze_x: float, gaze_y: float) -> bool:
        """Check if gaze is within calibrated screen bounds"""
        if self.screen_bounds is None:
            return True  # No calibration, assume on-screen
        
        return (
            self.screen_bounds['gaze_x_min'] <= gaze_x <= self.screen_bounds['gaze_x_max'] and
            self.screen_bounds['gaze_y_min'] <= gaze_y <= self.screen_bounds['gaze_y_max']
        )
    
    def get_direction_from_bounds(self, gaze_x: float, gaze_y: float) -> str:
        """Get direction relative to screen bounds"""
        if self.screen_bounds is None:
            return "UNKNOWN"
        
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
    
    def reset(self) -> None:
        """Reset calibration data"""
        self.calibration_data = []
        self.screen_bounds = None
