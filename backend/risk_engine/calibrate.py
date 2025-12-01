"""Calibration Module"""
from typing import Dict, Tuple


class Calibrator:
    """Screen boundary calibration"""
    
    def __init__(self):
        self.screen_bounds = None
    
    def is_within_bounds(self, gaze_x: float, gaze_y: float) -> bool:
        """Check if gaze is within screen bounds"""
        if self.screen_bounds is None:
            return True
        
        return (
            self.screen_bounds['x_min'] <= gaze_x <= self.screen_bounds['x_max'] and
            self.screen_bounds['y_min'] <= gaze_y <= self.screen_bounds['y_max']
        )
    
    def set_bounds(self, x_min: float, x_max: float, y_min: float, y_max: float):
        """Set screen bounds"""
        self.screen_bounds = {
            'x_min': x_min,
            'x_max': x_max,
            'y_min': y_min,
            'y_max': y_max
        }
