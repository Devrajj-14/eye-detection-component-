"""
PRECISION PHONE DETECTOR
Detects phones even if 30-40% visible, screen off, low light
Uses YOLOv8m with augmentation
"""
import cv2
import numpy as np
from collections import deque
from ultralytics import YOLO


class PrecisionPhoneDetector:
    def __init__(self):
        # Load YOLOv8m (medium model for better accuracy)
        try:
            self.model = YOLO('yolov8m.pt')
            print("✅ YOLOv8m loaded for precision detection")
        except:
            # Fallback to yolov8s
            self.model = YOLO('yolov8s.pt')
            print("⚠️ Using YOLOv8s (fallback)")
        
        # BALANCED SENSITIVITY detection settings
        self.CONFIDENCE_THRESHOLD = 0.25  # Balanced - reduce false positives
        self.MIN_AREA_PERCENTAGE = 0.0005  # Reasonable minimum size
        
        # Objects to detect
        self.PHONE_CLASSES = {'cell phone', 'mobile', 'smartphone', 'phone'}
        self.CHEATING_OBJECTS = {
            'cell phone', 'mobile', 'smartphone', 'phone',
            'tablet', 'ipad',
            'book', 'paper', 'notebook',
            'laptop',  # Configurable
            'remote',  # Can be phone-like
            'earphones', 'headphones', 'earbuds'
        }
        
        # Detection buffer (3-frame confirmation for accuracy)
        self.detection_buffer = deque(maxlen=3)
        
        # Partial phone detection
        self.edge_detection_enabled = True
    
    def detect_with_augmentation(self, frame):
        """
        Run YOLO with augmentation for better detection
        """
        # Run inference with augmentation
        results = self.model(
            frame,
            conf=self.CONFIDENCE_THRESHOLD,
            augment=True,  # Enable test-time augmentation
            verbose=False
        )
        
        detections = []
        frame_area = frame.shape[0] * frame.shape[1]
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                conf = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id].lower()
                
                # Only process cheating-relevant objects
                if not any(obj in class_name for obj in self.CHEATING_OBJECTS):
                    continue
                
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w = x2 - x1
                h = y2 - y1
                
                # Calculate area percentage
                box_area = w * h
                area_percentage = box_area / frame_area
                
                # Allow small objects (partial detection)
                if area_percentage < self.MIN_AREA_PERCENTAGE:
                    continue
                
                # Check if phone-like
                is_phone = any(p in class_name for p in self.PHONE_CLASSES)
                
                detections.append({
                    'class_name': class_name,
                    'confidence': conf,
                    'box': (x1, y1, w, h),
                    'is_phone': is_phone,
                    'is_partial': area_percentage < 0.01,  # Less than 1% = partial
                    'area_percentage': area_percentage
                })
                
                # Debug output for phone detections
                if is_phone:
                    partial_str = " (PARTIAL)" if area_percentage < 0.01 else ""
                    print(f"📱 PHONE DETECTED{partial_str}: {class_name} conf={conf:.3f} area={area_percentage:.4f}")
        
        return detections
    
    def detect_phone_edge(self, frame):
        """
        Detect phone edges/corners using edge detection
        For cases where phone is partially visible
        """
        if not self.edge_detection_enabled:
            return []
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        phone_edges = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Phone-sized contours
            if 1000 < area < 50000:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Phone-like aspect ratio (0.4 - 0.7)
                if 0.4 < aspect_ratio < 0.7:
                    phone_edges.append({
                        'class_name': 'phone_edge',
                        'confidence': 0.5,
                        'box': (x, y, w, h),
                        'is_phone': True,
                        'is_partial': True,
                        'detection_method': 'edge'
                    })
        
        return phone_edges
    
    def detect_phone_reflection(self, frame, face_box):
        """
        Detect phone reflection in glasses
        """
        if face_box is None:
            return []
        
        x, y, w, h = face_box
        
        # Check glasses area (upper face)
        glasses_region = frame[y:y+h//2, x:x+w]
        
        if glasses_region.size == 0:
            return []
        
        # Convert to HSV
        hsv = cv2.cvtColor(glasses_region, cv2.COLOR_BGR2HSV)
        _, _, v = cv2.split(hsv)
        
        # Detect very bright rectangular areas (phone screen reflection)
        bright = cv2.threshold(v, 240, 255, cv2.THRESH_BINARY)[1]
        
        contours, _ = cv2.findContours(bright, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        reflections = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:
                rx, ry, rw, rh = cv2.boundingRect(contour)
                aspect_ratio = rw / rh if rh > 0 else 0
                
                # Phone screen aspect ratio
                if 0.4 < aspect_ratio < 0.8:
                    reflections.append({
                        'class_name': 'phone_reflection',
                        'confidence': 0.6,
                        'box': (x + rx, y + ry, rw, rh),
                        'is_phone': True,
                        'is_partial': True,
                        'detection_method': 'reflection'
                    })
        
        return reflections
    
    def confirm_detection(self, detections):
        """
        Require 2 consecutive frames for confirmation (faster detection)
        Returns: confirmed detections
        """
        self.detection_buffer.append(detections)
        
        if len(self.detection_buffer) < 2:
            return []
        
        # Check if object detected in both frames
        confirmed = []
        
        for det in detections:
            # Check if similar detection in previous frame
            matches = 0
            for prev_dets in self.detection_buffer:
                for prev_det in prev_dets:
                    if prev_det['class_name'] == det['class_name']:
                        matches += 1
                        break
            
            if matches >= 2:
                confirmed.append(det)
        
        return confirmed
    
    def detect_all(self, frame, face_box=None):
        """
        Complete phone detection pipeline
        Returns: all confirmed detections
        """
        all_detections = []
        
        # 1. YOLO detection with augmentation
        yolo_dets = self.detect_with_augmentation(frame)
        all_detections.extend(yolo_dets)
        
        # 2. Edge detection for partial phones
        edge_dets = self.detect_phone_edge(frame)
        all_detections.extend(edge_dets)
        
        # 3. Reflection detection
        if face_box:
            reflection_dets = self.detect_phone_reflection(frame, face_box)
            all_detections.extend(reflection_dets)
        
        # 4. Confirm with 3-frame buffer
        confirmed = self.confirm_detection(all_detections)
        
        return confirmed, all_detections  # Return both for debugging
