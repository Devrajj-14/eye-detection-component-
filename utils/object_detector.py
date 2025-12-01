"""
YOLO-based object detection with auto-capture
"""
import cv2
import os
import json
from datetime import datetime
from ultralytics import YOLO


class ObjectDetector:
    def __init__(self, model_path="models/yolov8n.pt", confidence_threshold=0.25):
        """Initialize YOLO detector with balanced threshold"""
        self.confidence_threshold = confidence_threshold
        self.capture_dir = "captures"
        self.log_file = "captures/log.json"
        
        os.makedirs(self.capture_dir, exist_ok=True)
        
        try:
            self.model = YOLO(model_path)
            print(f"YOLO model loaded: {model_path}")
        except Exception as e:
            print(f"Error loading YOLO: {e}")
            self.model = None
    
    def detect(self, frame):
        """
        Detect objects in frame with ULTRA LOW threshold
        Returns: list of detections [{box, confidence, class_name}]
        """
        if self.model is None:
            return []
        
        # Run YOLO with maximum sensitivity
        results = self.model(frame, verbose=False, conf=self.confidence_threshold)
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                conf = float(box.conf[0])
                # Accept ALL detections above threshold
                if conf >= self.confidence_threshold:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    
                    # Calculate width and height
                    w = x2 - x1
                    h = y2 - y1
                    
                    detections.append({
                        'box': (x1, y1, w, h),
                        'confidence': conf,
                        'class_name': class_name
                    })
                    
                    # Debug output for ALL detected objects
                    print(f"🔍 DETECTED: {class_name} (confidence: {conf:.3f}, size: {w}x{h})")
                    
                    # Extra alert for phone-related objects
                    if 'phone' in class_name.lower() or 'cell' in class_name.lower() or 'remote' in class_name.lower():
                        print(f"📱 PHONE ALERT: {class_name} (confidence: {conf:.3f})")
        
        return detections
    
    def save_detection(self, frame, detections):
        """Save frame with detected objects"""
        if len(detections) == 0:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"object_{timestamp}.jpg"
        filepath = os.path.join(self.capture_dir, filename)
        
        cv2.imwrite(filepath, frame)
        
        # Log detection
        log_entry = {
            'timestamp': timestamp,
            'filename': filename,
            'detections': [
                {
                    'class': det['class_name'],
                    'confidence': det['confidence']
                }
                for det in detections
            ]
        }
        
        self._append_log(log_entry)
        
        return filepath
    
    def _append_log(self, entry):
        """Append detection to log file"""
        logs = []
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        logs.append(entry)
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def draw_detections(self, frame, detections):
        """Draw bounding boxes and labels for detections"""
        for det in detections:
            x, y, w, h = det['box']
            conf = det['confidence']
            label = f"{det['class_name']}: {conf:.2f}"
            
            # Draw box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
            
            # Draw label background
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame, (x, y - label_size[1] - 10), 
                         (x + label_size[0], y), (0, 255, 255), -1)
            
            # Draw label text
            cv2.putText(frame, label, (x, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
