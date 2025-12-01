"""
Screen Boundary Calibration System
Maps eye gaze to screen coordinates to detect when eyes go off-screen
"""
import cv2
import numpy as np
import json
import os
from datetime import datetime
from utils.face_tracker import FaceTracker
from utils.gaze_estimator import GazeEstimator


class ScreenCalibrator:
    def __init__(self):
        self.face_tracker = FaceTracker()
        self.gaze_estimator = GazeEstimator()
        
        # Calibration points (9-point calibration)
        self.calibration_points = [
            (0.1, 0.1),   # Top-left
            (0.5, 0.1),   # Top-center
            (0.9, 0.1),   # Top-right
            (0.1, 0.5),   # Middle-left
            (0.5, 0.5),   # Center
            (0.9, 0.5),   # Middle-right
            (0.1, 0.9),   # Bottom-left
            (0.5, 0.9),   # Bottom-center
            (0.9, 0.9),   # Bottom-right
        ]
        
        self.current_point_idx = 0
        self.calibration_data = []
        self.is_calibrated = False
        
        # Screen boundaries (will be learned)
        self.screen_bounds = {
            'gaze_x_min': None,
            'gaze_x_max': None,
            'gaze_y_min': None,
            'gaze_y_max': None,
            'head_yaw_range': None,
            'head_pitch_range': None
        }
    
    def get_current_calibration_point(self, screen_width, screen_height):
        """Get current calibration point in pixel coordinates"""
        if self.current_point_idx >= len(self.calibration_points):
            return None
        
        rel_x, rel_y = self.calibration_points[self.current_point_idx]
        return (int(rel_x * screen_width), int(rel_y * screen_height))
    
    def collect_calibration_sample(self, frame):
        """Collect gaze data for current calibration point"""
        face_boxes = self.face_tracker.detect_faces(frame)
        
        if len(face_boxes) == 0:
            return False, "No face detected"
        
        if len(face_boxes) > 1:
            return False, "Multiple faces detected"
        
        box = face_boxes[0]
        landmarks = self.face_tracker.get_landmarks(frame, box)
        
        if landmarks is None:
            return False, "No landmarks detected"
        
        # Get head pose
        head_pose = self.face_tracker.get_head_pose(landmarks, frame.shape)
        pitch, yaw, roll = head_pose
        
        # Get gaze
        gaze_vector, gaze_direction = self.gaze_estimator.estimate_gaze(
            frame, landmarks, head_pose
        )
        
        # Store calibration sample
        rel_x, rel_y = self.calibration_points[self.current_point_idx]
        
        sample = {
            'screen_point': (rel_x, rel_y),
            'gaze_vector': gaze_vector,
            'head_pose': head_pose,
            'gaze_direction': gaze_direction
        }
        
        self.calibration_data.append(sample)
        
        return True, "Sample collected"
    
    def next_point(self):
        """Move to next calibration point"""
        self.current_point_idx += 1
        return self.current_point_idx < len(self.calibration_points)
    
    def compute_screen_bounds(self):
        """Compute screen boundaries from calibration data"""
        if len(self.calibration_data) < 9:
            return False, "Not enough calibration data"
        
        # Extract gaze vectors
        gaze_x_values = []
        gaze_y_values = []
        yaw_values = []
        pitch_values = []
        
        for sample in self.calibration_data:
            gx, gy = sample['gaze_vector']
            pitch, yaw, roll = sample['head_pose']
            
            gaze_x_values.append(gx)
            gaze_y_values.append(gy)
            yaw_values.append(yaw)
            pitch_values.append(pitch)
        
        # Compute bounds with margin
        margin_x = 0.2  # 20% margin
        margin_y = 0.2
        
        gaze_x_range = max(gaze_x_values) - min(gaze_x_values)
        gaze_y_range = max(gaze_y_values) - min(gaze_y_values)
        
        self.screen_bounds = {
            'gaze_x_min': min(gaze_x_values) - gaze_x_range * margin_x,
            'gaze_x_max': max(gaze_x_values) + gaze_x_range * margin_x,
            'gaze_y_min': min(gaze_y_values) - gaze_y_range * margin_y,
            'gaze_y_max': max(gaze_y_values) + gaze_y_range * margin_y,
            'head_yaw_range': (min(yaw_values), max(yaw_values)),
            'head_pitch_range': (min(pitch_values), max(pitch_values))
        }
        
        self.is_calibrated = True
        
        return True, "Calibration complete"
    
    def is_gaze_on_screen(self, gaze_vector, head_pose):
        """Check if gaze is within screen boundaries"""
        if not self.is_calibrated:
            return True  # Default to on-screen if not calibrated
        
        gx, gy = gaze_vector
        pitch, yaw, roll = head_pose
        
        # Check gaze boundaries
        gaze_in_bounds = (
            self.screen_bounds['gaze_x_min'] <= gx <= self.screen_bounds['gaze_x_max'] and
            self.screen_bounds['gaze_y_min'] <= gy <= self.screen_bounds['gaze_y_max']
        )
        
        return gaze_in_bounds
    
    def get_off_screen_direction(self, gaze_vector, head_pose):
        """Determine which direction eyes are looking off-screen"""
        if not self.is_calibrated:
            return "UNKNOWN"
        
        gx, gy = gaze_vector
        
        # Determine primary direction
        if gx < self.screen_bounds['gaze_x_min']:
            return "LEFT_OF_SCREEN"
        elif gx > self.screen_bounds['gaze_x_max']:
            return "RIGHT_OF_SCREEN"
        elif gy < self.screen_bounds['gaze_y_min']:
            return "ABOVE_SCREEN"
        elif gy > self.screen_bounds['gaze_y_max']:
            return "BELOW_SCREEN"
        else:
            return "ON_SCREEN"
    
    def save_calibration(self, filename="calibration_data.json"):
        """Save calibration data to file"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'screen_bounds': self.screen_bounds,
            'calibration_points': self.calibration_points,
            'num_samples': len(self.calibration_data)
        }
        
        os.makedirs('calibration', exist_ok=True)
        filepath = os.path.join('calibration', filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def load_calibration(self, filename="calibration_data.json"):
        """Load calibration data from file"""
        filepath = os.path.join('calibration', filename)
        
        if not os.path.exists(filepath):
            return False, "Calibration file not found"
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.screen_bounds = data['screen_bounds']
            self.is_calibrated = True
            
            return True, "Calibration loaded"
        except Exception as e:
            return False, f"Error loading calibration: {e}"


def run_calibration():
    """Run interactive calibration"""
    calibrator = ScreenCalibrator()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    print("🎯 Screen Calibration System")
    print("=" * 50)
    print("Instructions:")
    print("1. Look at the RED circle on screen")
    print("2. Press SPACE to capture calibration point")
    print("3. Repeat for all 9 points")
    print("4. Press 'q' to quit")
    print("=" * 50)
    
    samples_per_point = 5
    current_samples = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        h, w = frame.shape[:2]
        
        # Get current calibration point
        point = calibrator.get_current_calibration_point(w, h)
        
        if point is None:
            # Calibration complete
            success, message = calibrator.compute_screen_bounds()
            
            if success:
                # Show completion message
                cv2.putText(frame, "CALIBRATION COMPLETE!", (w//2 - 200, h//2),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                cv2.putText(frame, "Press 's' to save, 'q' to quit", (w//2 - 200, h//2 + 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                cv2.imshow('Screen Calibration', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('s'):
                    filepath = calibrator.save_calibration()
                    print(f"✅ Calibration saved to: {filepath}")
                    print(f"📊 Screen Bounds: {calibrator.screen_bounds}")
                    break
                elif key == ord('q'):
                    break
            else:
                print(f"❌ {message}")
                break
            
            continue
        
        # Draw calibration point
        px, py = point
        cv2.circle(frame, (px, py), 30, (0, 0, 255), -1)
        cv2.circle(frame, (px, py), 35, (255, 255, 255), 3)
        
        # Draw instructions
        point_num = calibrator.current_point_idx + 1
        cv2.putText(frame, f"Point {point_num}/9 - Look at RED circle", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Samples: {current_samples}/{samples_per_point}", (20, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, "Press SPACE to capture", (20, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Process face and gaze
        face_boxes = calibrator.face_tracker.detect_faces(frame)
        
        if len(face_boxes) == 1:
            box = face_boxes[0]
            landmarks = calibrator.face_tracker.get_landmarks(frame, box)
            
            if landmarks is not None:
                # Draw face tracking
                x, y, w_box, h_box = box
                cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
                
                # Get head pose and gaze
                head_pose = calibrator.face_tracker.get_head_pose(landmarks, frame.shape)
                gaze_result = calibrator.gaze_estimator.estimate_gaze(
                    frame, landmarks, head_pose
                )
                
                # Handle both old and new return formats
                if len(gaze_result) == 4:
                    gaze_vector, gaze_direction, _, _ = gaze_result
                else:
                    gaze_vector, gaze_direction = gaze_result
                
                # Draw gaze
                calibrator.gaze_estimator.draw_gaze(frame, landmarks, gaze_vector, gaze_direction)
                
                cv2.putText(frame, "✓ Face detected - Ready", (20, h - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "✗ Position your face in frame", (20, h - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.imshow('Screen Calibration', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):
            # Capture sample
            success, message = calibrator.collect_calibration_sample(frame)
            
            if success:
                current_samples += 1
                print(f"✓ Sample {current_samples}/{samples_per_point} captured for point {point_num}")
                
                if current_samples >= samples_per_point:
                    # Move to next point
                    has_more = calibrator.next_point()
                    current_samples = 0
                    
                    if not has_more:
                        print("🎉 All points captured! Computing bounds...")
            else:
                print(f"✗ {message}")
        
        elif key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_calibration()
