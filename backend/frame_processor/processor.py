"""
Frame Processor
Handles all ML-based detection
"""
import cv2
import numpy as np
from typing import Dict, List
import mediapipe as mp
from ultralytics import YOLO


class FrameProcessor:
    """Main frame processor"""
    
    def __init__(self):
        self.face_detection = None
        self.face_mesh = None
        self.yolo_model = None
        self.initialized = False
    
    def initialize(self):
        """Load all models"""
        print("Loading MediaPipe Face Detection...")
        self.face_detection = mp.solutions.face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.5
        )
        
        print("Loading MediaPipe Face Mesh...")
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=3,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        print("Loading YOLO...")
        try:
            self.yolo_model = YOLO('models/yolov8n.pt')
        except:
            print("⚠️ YOLO model not found, object detection disabled")
            self.yolo_model = None
        
        self.initialized = True
        print("✅ All models loaded")
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """Process a single frame"""
        if not self.initialized:
            raise RuntimeError("Processor not initialized")
        
        events = []
        objects = []
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 1. Face Detection
        face_results = self.face_detection.process(rgb_frame)
        face_count = 0
        
        if face_results.detections:
            face_count = len(face_results.detections)
            
            if face_count == 0:
                events.append("NO_FACE")
            elif face_count > 1:
                events.append("MULTIPLE_FACES")
        
        # 2. Gaze Tracking (using face mesh)
        gaze_direction = "center"
        attention = 100
        
        if face_count == 1:
            mesh_results = self.face_mesh.process(rgb_frame)
            
            if mesh_results.multi_face_landmarks:
                landmarks = mesh_results.multi_face_landmarks[0]
                
                # Estimate gaze from iris landmarks
                gaze_direction = self._estimate_gaze(landmarks, frame.shape)
                
                if gaze_direction in ['left', 'right', 'down', 'up']:
                    events.append("LOOKING_AWAY")
                    attention = 60
        
        # 3. Object Detection
        if self.yolo_model is not None:
            detections = self.yolo_model(frame, verbose=False, conf=0.25)
            
            for result in detections:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = self.yolo_model.names[class_id].lower()
                    
                    # Check for cheating objects
                    if 'phone' in class_name or 'cell' in class_name:
                        objects.append(class_name)
                        events.append("PHONE_DETECTED")
                    elif 'book' in class_name or 'paper' in class_name:
                        objects.append(class_name)
                        events.append("SUSPICIOUS_OBJECT")
                    elif 'laptop' in class_name or 'tablet' in class_name:
                        objects.append(class_name)
                        events.append("SUSPICIOUS_OBJECT")
        
        return {
            'faces': face_count,
            'gaze': gaze_direction,
            'attention': attention,
            'objects': objects,
            'events': events
        }
    
    def _estimate_gaze(self, landmarks, frame_shape) -> str:
        """Estimate gaze direction from face mesh"""
        # Get iris landmarks (468-477 for left, 473-478 for right)
        h, w = frame_shape[:2]
        
        # Left eye center
        left_eye_center = landmarks.landmark[468]
        left_x = left_eye_center.x
        left_y = left_eye_center.y
        
        # Right eye center  
        right_eye_center = landmarks.landmark[473]
        right_x = right_eye_center.x
        right_y = right_eye_center.y
        
        # Average
        avg_x = (left_x + right_x) / 2
        avg_y = (left_y + right_y) / 2
        
        # Classify (relative to center 0.5, 0.5)
        threshold = 0.05
        
        if avg_x < 0.5 - threshold:
            return "left"
        elif avg_x > 0.5 + threshold:
            return "right"
        elif avg_y < 0.5 - threshold:
            return "up"
        elif avg_y > 0.5 + threshold:
            return "down"
        else:
            return "center"
