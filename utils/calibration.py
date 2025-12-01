"""
9-point calibration system for gaze tracking
"""
import cv2
import numpy as np
import json
import os
from sklearn.linear_model import Ridge


class GazeCalibration:
    def __init__(self, screen_width=1920, screen_height=1080):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.calibration_points = self._generate_calibration_points()
        self.current_point_idx = 0
        self.calibration_data = []
        self.is_calibrating = False
        self.model_x = None
        self.model_y = None
        self.calibration_file = "calibration/calibration.json"
        
        # Load existing calibration if available
        self.load_calibration()
    
    def _generate_calibration_points(self):
        """Generate 9-point grid for calibration - covers full screen"""
        points = []
        # Use corners and edges to define screen boundaries
        for y in [0.1, 0.5, 0.9]:  # Top, middle, bottom
            for x in [0.1, 0.5, 0.9]:  # Left, middle, right
                points.append((
                    int(x * self.screen_width),
                    int(y * self.screen_height)
                ))
        return points
    
    def start_calibration(self):
        """Start calibration process"""
        self.is_calibrating = True
        self.current_point_idx = 0
        self.calibration_data = []
    
    def get_current_point(self):
        """Get current calibration point"""
        if not self.is_calibrating or self.current_point_idx >= len(self.calibration_points):
            return None
        return self.calibration_points[self.current_point_idx]
    
    def add_calibration_sample(self, eye_features):
        """
        Add calibration sample
        eye_features: dict with 'left_iris', 'right_iris', 'head_pose', 'landmarks'
        """
        if not self.is_calibrating:
            return False
        
        current_point = self.get_current_point()
        if current_point is None:
            return False
        
        # Extract features
        features = self._extract_features(eye_features)
        
        self.calibration_data.append({
            'screen_x': current_point[0],
            'screen_y': current_point[1],
            'features': features
        })
        
        self.current_point_idx += 1
        
        # Check if calibration complete
        if self.current_point_idx >= len(self.calibration_points):
            self.finish_calibration()
            return True
        
        return False
    
    def _extract_features(self, eye_features):
        """Extract feature vector from eye data"""
        features = []
        
        # Left iris position (normalized)
        if 'left_iris' in eye_features and eye_features['left_iris'] is not None:
            features.extend([
                eye_features['left_iris'][0] / self.screen_width,
                eye_features['left_iris'][1] / self.screen_height
            ])
        else:
            features.extend([0.5, 0.5])
        
        # Right iris position (normalized)
        if 'right_iris' in eye_features and eye_features['right_iris'] is not None:
            features.extend([
                eye_features['right_iris'][0] / self.screen_width,
                eye_features['right_iris'][1] / self.screen_height
            ])
        else:
            features.extend([0.5, 0.5])
        
        # Head pose
        if 'head_pose' in eye_features:
            pitch, yaw, roll = eye_features['head_pose']
            features.extend([pitch / 90.0, yaw / 90.0, roll / 90.0])
        else:
            features.extend([0, 0, 0])
        
        return features
    
    def finish_calibration(self):
        """Build regression model from calibration data"""
        self.is_calibrating = False
        
        if len(self.calibration_data) < 5:
            print("Not enough calibration samples")
            return
        
        # Prepare training data
        X = np.array([sample['features'] for sample in self.calibration_data])
        y_x = np.array([sample['screen_x'] for sample in self.calibration_data])
        y_y = np.array([sample['screen_y'] for sample in self.calibration_data])
        
        # Train models
        self.model_x = Ridge(alpha=1.0)
        self.model_y = Ridge(alpha=1.0)
        
        self.model_x.fit(X, y_x)
        self.model_y.fit(X, y_y)
        
        # Save calibration
        self.save_calibration()
        
        print("Calibration complete!")
    
    def predict_gaze_point(self, eye_features):
        """Predict screen gaze point from eye features"""
        if self.model_x is None or self.model_y is None:
            return None
        
        features = self._extract_features(eye_features)
        X = np.array([features])
        
        gaze_x = int(self.model_x.predict(X)[0])
        gaze_y = int(self.model_y.predict(X)[0])
        
        # Clamp to screen bounds
        gaze_x = max(0, min(self.screen_width, gaze_x))
        gaze_y = max(0, min(self.screen_height, gaze_y))
        
        return (gaze_x, gaze_y)
    
    def save_calibration(self):
        """Save calibration to file"""
        os.makedirs(os.path.dirname(self.calibration_file), exist_ok=True)
        
        data = {
            'screen_width': self.screen_width,
            'screen_height': self.screen_height,
            'calibration_data': self.calibration_data,
            'model_x_coef': self.model_x.coef_.tolist() if self.model_x else None,
            'model_x_intercept': float(self.model_x.intercept_) if self.model_x else None,
            'model_y_coef': self.model_y.coef_.tolist() if self.model_y else None,
            'model_y_intercept': float(self.model_y.intercept_) if self.model_y else None,
        }
        
        with open(self.calibration_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_calibration(self):
        """Load calibration from file"""
        if not os.path.exists(self.calibration_file):
            return False
        
        try:
            with open(self.calibration_file, 'r') as f:
                data = json.load(f)
            
            self.screen_width = data['screen_width']
            self.screen_height = data['screen_height']
            self.calibration_data = data['calibration_data']
            
            if data['model_x_coef'] and data['model_y_coef']:
                self.model_x = Ridge(alpha=1.0)
                self.model_y = Ridge(alpha=1.0)
                
                # Reconstruct models
                self.model_x.coef_ = np.array(data['model_x_coef'])
                self.model_x.intercept_ = data['model_x_intercept']
                self.model_y.coef_ = np.array(data['model_y_coef'])
                self.model_y.intercept_ = data['model_y_intercept']
                
                print("Calibration loaded successfully")
                return True
        except Exception as e:
            print(f"Error loading calibration: {e}")
        
        return False
    
    def draw_calibration_point(self, frame):
        """Draw current calibration point on frame"""
        point = self.get_current_point()
        if point is None:
            return
        
        # Scale point to frame size
        h, w = frame.shape[:2]
        x = int(point[0] * w / self.screen_width)
        y = int(point[1] * h / self.screen_height)
        
        # Draw target
        cv2.circle(frame, (x, y), 20, (0, 0, 255), -1)
        cv2.circle(frame, (x, y), 25, (255, 255, 255), 2)
        
        # Draw progress
        progress = f"{self.current_point_idx + 1}/{len(self.calibration_points)}"
        cv2.putText(frame, progress, (x - 30, y - 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Instructions
        cv2.putText(frame, "Look at the red dot", (w // 2 - 150, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
