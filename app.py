"""
Main application controller
"""
import cv2
import sys
import time
import numpy as np
from PyQt5.QtWidgets import QApplication

from utils.face_tracker import FaceTracker
from utils.gaze_estimator import GazeEstimator
from utils.calibration import GazeCalibration
from utils.object_detector import ObjectDetector
from utils.id_tracker import PersonTracker
from ui.interface import MainWindow


class OpenFaceApp:
    def __init__(self):
        # Initialize components
        self.face_tracker = FaceTracker()
        self.gaze_estimator = GazeEstimator()
        self.calibration = GazeCalibration()
        self.object_detector = ObjectDetector()
        self.person_tracker = PersonTracker()
        
        # Camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # State
        self.current_frame = None
        self.is_running = True
        self.detection_enabled = False
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # Calibration timing
        self.calibration_start_time = None
        self.calibration_sample_duration = 1.0  # seconds per point
    
    def process_frame(self):
        """Main processing loop"""
        ret, frame = self.cap.read()
        if not ret:
            return
        
        self.frame_count += 1
        
        # Calculate FPS
        elapsed = time.time() - self.start_time
        if elapsed > 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()
        
        # Detect faces
        face_boxes = self.face_tracker.detect_faces(frame)
        
        # Update person tracker
        tracked_objects = self.person_tracker.update(face_boxes)
        
        # Process each face
        people_data = []
        for box in face_boxes:
            person_id = self.person_tracker.get_id_for_box(box)
            
            # Get landmarks
            landmarks = self.face_tracker.get_landmarks(frame, box)
            
            # Get head pose
            head_pose = self.face_tracker.get_head_pose(landmarks, frame.shape)
            
            # Estimate gaze
            gaze_vector, gaze_direction = self.gaze_estimator.estimate_gaze(
                frame, landmarks, head_pose
            )
            
            # Draw face box
            x, y, w, h = box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw person ID
            if person_id is not None:
                cv2.putText(frame, f"ID: {person_id}", (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Draw landmarks
            self.face_tracker.draw_landmarks(frame, landmarks)
            
            # Draw head pose
            self.face_tracker.draw_head_pose(frame, landmarks, head_pose)
            
            # Draw gaze
            self.gaze_estimator.draw_gaze(frame, landmarks, gaze_vector, gaze_direction)
            
            # Store person data
            people_data.append({
                'id': person_id,
                'face_box': box,
                'gaze_direction': gaze_direction,
                'landmarks': landmarks.tolist() if landmarks is not None else None,
                'head_pose': head_pose
            })
            
            # Handle calibration
            if self.calibration.is_calibrating and landmarks is not None:
                # Collect calibration sample after delay
                if self.calibration_start_time is None:
                    self.calibration_start_time = time.time()
                
                elapsed = time.time() - self.calibration_start_time
                if elapsed >= self.calibration_sample_duration:
                    # Extract eye features for calibration
                    left_eye_region, left_box = self.gaze_estimator.get_eye_region(
                        frame, landmarks, self.gaze_estimator.LEFT_EYE
                    )
                    right_eye_region, right_box = self.gaze_estimator.get_eye_region(
                        frame, landmarks, self.gaze_estimator.RIGHT_EYE
                    )
                    
                    left_iris = self.gaze_estimator.get_iris_center(left_eye_region)
                    right_iris = self.gaze_estimator.get_iris_center(right_eye_region)
                    
                    # Convert to global coordinates
                    left_iris_global = None
                    right_iris_global = None
                    
                    if left_iris and left_box:
                        left_iris_global = (left_box[0] + left_iris[0], left_box[1] + left_iris[1])
                    if right_iris and right_box:
                        right_iris_global = (right_box[0] + right_iris[0], right_box[1] + right_iris[1])
                    
                    eye_features = {
                        'left_iris': left_iris_global,
                        'right_iris': right_iris_global,
                        'head_pose': head_pose,
                        'landmarks': landmarks
                    }
                    
                    complete = self.calibration.add_calibration_sample(eye_features)
                    self.calibration_start_time = None
                    
                    if complete:
                        # Calibration finished
                        pass
        
        # Draw calibration point if active
        if self.calibration.is_calibrating:
            self.calibration.draw_calibration_point(frame)
        
        # Object detection
        if self.detection_enabled:
            detections = self.object_detector.detect(frame)
            
            if len(detections) > 0:
                self.object_detector.draw_detections(frame, detections)
                self.object_detector.save_detection(frame, detections)
        
        # Draw FPS
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Draw people count
        cv2.putText(frame, f"People: {len(face_boxes)}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        self.current_frame = frame
    
    def get_current_frame(self):
        """Get current processed frame"""
        return self.current_frame
    
    def get_status(self):
        """Get current status string"""
        status_parts = []
        
        if self.calibration.is_calibrating:
            point = self.calibration.current_point_idx + 1
            total = len(self.calibration.calibration_points)
            status_parts.append(f"Calibrating: {point}/{total}")
        elif self.calibration.model_x is not None:
            status_parts.append("Calibration Complete ✓")
        
        if self.detection_enabled:
            status_parts.append("Object Detection: ON")
        
        status_parts.append(f"FPS: {self.fps:.1f}")
        
        return " | ".join(status_parts) if status_parts else "Ready"
    
    def start_calibration(self):
        """Start calibration process"""
        self.calibration.start_calibration()
        self.calibration_start_time = None
    
    def stop_calibration(self):
        """Stop calibration process"""
        self.calibration.is_calibrating = False
    
    def is_calibrating(self):
        """Check if calibration is active"""
        return self.calibration.is_calibrating
    
    def start_detection(self):
        """Enable object detection"""
        self.detection_enabled = True
    
    def stop_detection(self):
        """Disable object detection"""
        self.detection_enabled = False
    
    def is_detecting(self):
        """Check if detection is enabled"""
        return self.detection_enabled
    
    def cleanup(self):
        """Cleanup resources"""
        self.is_running = False
        if self.cap:
            self.cap.release()
    
    def run(self):
        """Main application loop"""
        app = QApplication(sys.argv)
        window = MainWindow(self)
        window.show()
        
        # Process frames in background
        import threading
        
        def process_loop():
            while self.is_running:
                self.process_frame()
                time.sleep(0.01)
        
        thread = threading.Thread(target=process_loop, daemon=True)
        thread.start()
        
        sys.exit(app.exec_())


if __name__ == "__main__":
    app = OpenFaceApp()
    app.run()
