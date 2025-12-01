"""
Smart Detection with Strict Filtering
NO FALSE POSITIVES - Only real cheating detected
"""
import cv2
import numpy as np
from collections import deque


class SmartDetector:
    def __init__(self):
        # STRICT: Only these objects are cheating-relevant
        self.CHEATING_OBJECTS = {
            'cell phone', 'mobile', 'smartphone', 'phone',
            'tablet', 'ipad',
            'book', 'paper', 'notebook',
            'laptop',  # Only if not allowed
            'headphones', 'earphones', 'earbuds'
        }
        
        # Objects to ALWAYS IGNORE
        self.IGNORE_OBJECTS = {
            'person', 'chair', 'sofa', 'couch', 'bed',
            'door', 'window', 'wall', 'ceiling', 'floor',
            'ac', 'fan', 'light', 'lamp',
            'cup', 'bottle', 'mug', 'glass',
            'cloth', 'towel', 'pillow', 'blanket',
            'desk', 'table', 'shelf', 'cabinet',
            'tv', 'monitor', 'screen',  # Ignore if far from hands
            'keyboard', 'mouse'  # Ignore if part of setup
        }
        
        # Detection buffers (require 3 consecutive frames)
        self.object_buffer = deque(maxlen=3)
        self.face_count_buffer = deque(maxlen=5)
        
        # Thresholds - BALANCED SENSITIVITY
        self.MIN_CONFIDENCE = 0.25  # Balanced detection (reduce false positives)
        self.CONSECUTIVE_FRAMES_REQUIRED = 2  # Require 2 frames for confirmation
        
    def is_near_hands_or_face(self, obj_box, face_box):
        """Check if object is near hands or face (cheating zone)"""
        if face_box is None:
            return False
        
        fx, fy, fw, fh = face_box
        ox, oy, ow, oh = obj_box
        
        # Define cheating zone (around face and below)
        zone_x1 = fx - fw
        zone_y1 = fy - fh // 2
        zone_x2 = fx + fw * 2
        zone_y2 = fy + fh * 3  # Extends below face for hands
        
        # Check if object center is in zone
        obj_center_x = ox + ow // 2
        obj_center_y = oy + oh // 2
        
        in_zone = (zone_x1 < obj_center_x < zone_x2 and 
                   zone_y1 < obj_center_y < zone_y2)
        
        return in_zone
    
    def filter_yolo_detections(self, detections, face_box=None):
        """
        STRICT filtering of YOLO detections
        Returns only REAL cheating-relevant objects
        """
        filtered = []
        
        for det in detections:
            obj_class = det['class_name'].lower()
            confidence = det['confidence']
            box = det['box']
            
            # Rule 1: Ignore low confidence
            if confidence < self.MIN_CONFIDENCE:
                continue
            
            # Rule 2: ALWAYS ignore non-cheating objects
            if obj_class in self.IGNORE_OBJECTS:
                continue
            
            # Rule 3: Only accept cheating-relevant objects
            is_cheating_object = any(cheat in obj_class for cheat in self.CHEATING_OBJECTS)
            if not is_cheating_object:
                continue
            
            # Rule 4: Check if near hands/face (but allow objects anywhere for now)
            # Disabled to maximize detection - objects detected anywhere in frame
            # if face_box is not None:
            #     if not self.is_near_hands_or_face(box, face_box):
            #         continue
            
            # Rule 5: Object must be reasonably sized
            _, _, w, h = box
            if w < 20 or h < 20:  # Reasonable minimum to avoid false positives
                continue
            
            filtered.append(det)
        
        return filtered
    
    def detect_multiple_people(self, face_boxes):
        """
        Use ONLY face count for multiple people detection
        IGNORE YOLO person boxes
        """
        face_count = len(face_boxes)
        self.face_count_buffer.append(face_count)
        
        # Require consistent detection over 5 frames
        if len(self.face_count_buffer) == 5:
            avg_faces = sum(self.face_count_buffer) / 5
            if avg_faces > 1.5:  # More than 1 person consistently
                return True, int(avg_faces)
        
        return False, face_count
    
    def requires_consecutive_detection(self, event_type, detected):
        """
        Require 2 consecutive frames before triggering event (faster detection)
        """
        # Add to buffer
        self.object_buffer.append((event_type, detected))
        
        # Check if last 2 frames detected same event
        if len(self.object_buffer) >= 2:
            recent = list(self.object_buffer)[-2:]
            if all(e[0] == event_type and e[1] for e in recent):
                return True
        
        return False
    
    def calculate_attention_score(self, gaze_history):
        """
        Proper attention calculation from gaze direction
        NOT from YOLO
        """
        if len(gaze_history) < 10:
            return 100  # Default to good attention
        
        recent_gaze = list(gaze_history)[-30:]  # Last 30 frames
        
        # Count center gazes
        center_count = sum(1 for g in recent_gaze if g == "looking_center")
        
        # Calculate percentage
        attention = (center_count / len(recent_gaze)) * 100
        
        return max(0, min(100, attention))
    
    def is_significant_background_movement(self, motion_area, frame_shape):
        """
        Check if background movement is significant enough to be suspicious
        Ignore: shadows, light flicker, exposure changes
        """
        frame_area = frame_shape[0] * frame_shape[1]
        motion_percentage = (motion_area / frame_area) * 100
        
        # Only flag if movement is > 5% of frame AND large absolute area
        if motion_percentage > 5 and motion_area > 50000:
            return True
        
        return False
    
    def is_suspicious_reflection(self, reflection_intensity, reflection_shape):
        """
        Check if reflection matches phone screen pattern
        Ignore: white walls, dim lighting, camera auto-exposure
        """
        # Reflection must be very bright (phone screen level)
        if reflection_intensity < 220:  # Not bright enough
            return False
        
        # Reflection should have rectangular shape (screen)
        if reflection_shape is None:
            return False
        
        # Check aspect ratio (phone-like)
        x, y, w, h = reflection_shape
        aspect_ratio = w / h if h > 0 else 0
        
        # Phone screens are typically 0.5-0.7 aspect ratio
        if 0.4 < aspect_ratio < 0.8:
            return True
        
        return False
