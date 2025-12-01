"""
Object Detection Module
Uses YOLO for detecting phones and other objects
"""
import cv2
import numpy as np
from typing import List, Dict
from ultralytics import YOLO


class ObjectDetector:
    """YOLO-based object detection"""
    
    def __init__(self):
        self.model = None
        self.confidence_threshold = 0.25
        self.cheating_objects = {
            'cell phone', 'mobile', 'smartphone', 'phone',
            'tablet', 'ipad', 'book', 'paper', 'notebook',
            'laptop', 'computer'
        }
    
    async def load_models(self):
        """Load YOLO model"""
        try:
            self.model = YOLO('models/yolov8n.pt')
            print("✅ YOLO model loaded")
        except Exception as e:
            print(f"⚠️ Warning: Could not load YOLO model: {e}")
            self.model = None
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in frame
        
        Args:
            frame: BGR image
        
        Returns:
            List of detections with class, confidence, box, and partial flag
        """
        if self.model is None:
            return []
        
        # Run YOLO
        results = self.model(frame, verbose=False, conf=self.confidence_threshold)
        
        detections = []
        frame_area = frame.shape[0] * frame.shape[1]
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                conf = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id].lower()
                
                # Only process cheating-relevant objects
                if not any(obj in class_name for obj in self.cheating_objects):
                    continue
                
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w = x2 - x1
                h = y2 - y1
                
                # Calculate if partial (< 50% of typical phone size)
                box_area = w * h
                area_percentage = box_area / frame_area
                is_partial = area_percentage < 0.01  # Less than 1% of frame
                
                detections.append({
                    'class_name': class_name,
                    'confidence': conf,
                    'box': (x1, y1, w, h),
                    'is_partial': is_partial,
                    'area_percentage': area_percentage
                })
        
        return detections
