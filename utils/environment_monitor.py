"""
Environment Monitoring Module
Detects background changes, reflections, and suspicious objects
"""
import cv2
import numpy as np
from collections import deque


class EnvironmentMonitor:
    def __init__(self):
        self.background_model = None
        self.previous_frame = None
        self.motion_history = deque(maxlen=30)
        self.lighting_history = deque(maxlen=50)
        
        # Detection thresholds
        self.MOTION_THRESHOLD = 5000
        self.LIGHTING_CHANGE_THRESHOLD = 20
        
        # Event counters
        self.background_changes = 0
        self.lighting_anomalies = 0
        self.motion_events = 0
        
    def initialize_background(self, frame):
        """Initialize background model"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.background_model = cv2.GaussianBlur(gray, (21, 21), 0)
        self.previous_frame = gray.copy()
    
    def detect_background_change(self, frame):
        """
        Detect SIGNIFICANT background changes ONLY
        Ignore: shadows, light flicker, exposure changes
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.background_model is None:
            self.initialize_background(frame)
            return False, None
        
        # Compute difference
        frame_delta = cv2.absdiff(self.background_model, gray)
        # Higher threshold to ignore small changes
        thresh = cv2.threshold(frame_delta, 40, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check for significant changes
        total_motion = sum(cv2.contourArea(c) for c in contours)
        self.motion_history.append(total_motion)
        
        # MUCH higher threshold - only flag major movement
        frame_area = frame.shape[0] * frame.shape[1]
        motion_percentage = (total_motion / frame_area) * 100
        
        # Only flag if > 5% of frame AND large absolute area
        if motion_percentage > 5 and total_motion > 50000:
            self.background_changes += 1
            self.motion_events += 1
            return True, contours
        
        # Update background model slowly
        self.background_model = cv2.addWeighted(self.background_model, 0.95, gray, 0.05, 0)
        
        return False, None
    
    def detect_lighting_change(self, frame):
        """
        Detect sudden lighting changes (screen reflection)
        IGNORE: normal exposure changes, white walls
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        
        self.lighting_history.append(avg_brightness)
        
        if len(self.lighting_history) < 10:
            return False
        
        recent = list(self.lighting_history)[-10:]
        brightness_change = max(recent) - min(recent)
        
        # MUCH higher threshold - only flag dramatic changes
        if brightness_change > 40:  # Increased from 20
            self.lighting_anomalies += 1
            return True
        
        return False
    
    def detect_reflection(self, frame, face_box):
        """
        Detect reflections ONLY if matches phone screen pattern
        IGNORE: white walls, normal lighting, camera exposure
        """
        if face_box is None:
            return False, None
        
        x, y, w, h = face_box
        
        # Check only near glasses area (upper face)
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(frame.shape[1], x + w)
        y2 = min(frame.shape[0], y + h // 2)  # Only upper half
        
        region = frame[y1:y2, x1:x2]
        
        if region.size == 0:
            return False, None
        
        # Convert to HSV for better detection
        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        
        # Detect VERY bright spots only (phone screen level)
        _, _, v = cv2.split(hsv)
        bright_spots = cv2.threshold(v, 230, 255, cv2.THRESH_BINARY)[1]  # Higher threshold
        
        # Count bright pixels
        bright_pixel_count = np.sum(bright_spots > 0)
        total_pixels = region.shape[0] * region.shape[1]
        
        # Much stricter - must be > 10% AND have rectangular shape
        if bright_pixel_count > total_pixels * 0.10:
            # Check if bright area has rectangular shape (phone screen)
            contours, _ = cv2.findContours(bright_spots, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest)
                aspect_ratio = w / h if h > 0 else 0
                # Phone-like aspect ratio
                if 0.4 < aspect_ratio < 0.8:
                    return True, bright_spots
        
        return False, None
    
    def detect_desk_objects(self, frame, face_box):
        """
        Detect NEW objects on desk
        IGNORE: shoulders, shadows, color patches, noise
        """
        if face_box is None:
            return []
        
        x, y, w, h = face_box
        
        # Define desk region (below face, but not too low)
        desk_y = y + h + 20  # Start below face
        desk_y_end = min(frame.shape[0], desk_y + h * 2)  # Limited region
        desk_region = frame[desk_y:desk_y_end, :]
        
        if desk_region.size == 0:
            return []
        
        # Simple motion detection in desk area
        if self.previous_frame is not None:
            prev_desk = self.previous_frame[desk_y:desk_y_end, :]
            
            if prev_desk.shape == desk_region.shape:
                gray_current = cv2.cvtColor(desk_region, cv2.COLOR_BGR2GRAY)
                gray_prev = cv2.cvtColor(prev_desk, cv2.COLOR_BGR2GRAY)
                
                diff = cv2.absdiff(gray_current, gray_prev)
                # Higher threshold to ignore small movements
                _, thresh = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)
                
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # MUCH stricter filtering - must be large and persistent
                objects = [c for c in contours if cv2.contourArea(c) > 2000]  # Increased from 500
                return objects
        
        self.previous_frame = frame.copy()
        return []
    
    def analyze_frame(self, frame, face_box=None):
        """Analyze frame for environment anomalies"""
        events = []
        
        # Check background changes
        bg_changed, contours = self.detect_background_change(frame)
        if bg_changed:
            events.append({
                'type': 'BACKGROUND_CHANGE',
                'severity': 'medium',
                'description': 'Significant background movement detected'
            })
        
        # Check lighting changes
        if self.detect_lighting_change(frame):
            events.append({
                'type': 'LIGHTING_ANOMALY',
                'severity': 'low',
                'description': 'Sudden lighting change (possible screen reflection)'
            })
        
        # Check reflections if face detected
        if face_box is not None:
            has_reflection, _ = self.detect_reflection(frame, face_box)
            if has_reflection:
                events.append({
                    'type': 'REFLECTION_DETECTED',
                    'severity': 'medium',
                    'description': 'Bright reflection detected (glasses/screen)'
                })
            
            # Check desk objects
            desk_objects = self.detect_desk_objects(frame, face_box)
            if len(desk_objects) > 0:
                events.append({
                    'type': 'DESK_OBJECT_MOVEMENT',
                    'severity': 'high',
                    'description': f'Object movement on desk ({len(desk_objects)} objects)'
                })
        
        return events
    
    def get_environment_summary(self):
        """Get summary of environment monitoring"""
        return {
            'background_changes': self.background_changes,
            'lighting_anomalies': self.lighting_anomalies,
            'motion_events': self.motion_events,
            'avg_motion': np.mean(list(self.motion_history)) if self.motion_history else 0
        }
    
    def reset(self):
        """Reset environment monitoring state"""
        self.background_model = None
        self.previous_frame = None
        self.background_changes = 0
        self.lighting_anomalies = 0
        self.motion_events = 0
        self.motion_history.clear()
        self.lighting_history.clear()
