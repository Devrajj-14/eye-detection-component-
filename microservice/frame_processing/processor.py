"""
Main Frame Processor
Coordinates all detection modules
"""
import cv2
import numpy as np
from typing import Dict, List, Optional
import asyncio

from .face_detector import FaceDetector
from .gaze_tracker import GazeTracker
from .object_detector import ObjectDetector
from .behavior_analyzer import BehaviorAnalyzer


class FrameProcessor:
    """
    Main frame processor that coordinates all detection modules
    """
    
    def __init__(self):
        self.face_detector: Optional[FaceDetector] = None
        self.gaze_tracker: Optional[GazeTracker] = None
        self.object_detector: Optional[ObjectDetector] = None
        self.behavior_analyzer: Optional[BehaviorAnalyzer] = None
        self._ready = False
    
    async def initialize(self):
        """Initialize all ML models"""
        print("Loading face detector...")
        self.face_detector = FaceDetector()
        await self.face_detector.load_models()
        
        print("Loading gaze tracker...")
        self.gaze_tracker = GazeTracker()
        await self.gaze_tracker.load_models()
        
        print("Loading object detector...")
        self.object_detector = ObjectDetector()
        await self.object_detector.load_models()
        
        print("Loading behavior analyzer...")
        self.behavior_analyzer = BehaviorAnalyzer()
        
        self._ready = True
        print("All models loaded successfully!")
    
    def is_ready(self) -> bool:
        """Check if all models are loaded"""
        return self._ready
    
    async def process_frame(self, frame: np.ndarray) -> Dict:
        """
        Process a single frame and return analysis
        
        Args:
            frame: BGR image as numpy array
        
        Returns:
            Dictionary with analysis results
        """
        if not self._ready:
            raise RuntimeError("Models not initialized")
        
        events = []
        
        # 1. Face Detection
        faces = self.face_detector.detect_faces(frame)
        face_count = len(faces)
        
        if face_count == 0:
            events.append("NO_FACE")
        elif face_count > 1:
            events.append("MULTIPLE_FACES")
        
        # 2. Gaze Tracking (if face detected)
        gaze_direction = "unknown"
        attention = 100
        
        if face_count == 1:
            face_box = faces[0]
            landmarks = self.face_detector.get_landmarks(frame, face_box)
            
            if landmarks is not None:
                # Get gaze
                gaze_result = self.gaze_tracker.estimate_gaze(frame, landmarks)
                gaze_direction = gaze_result['direction']
                
                # Check if looking away
                if gaze_direction in ['looking_left', 'looking_right', 'looking_down', 'looking_up']:
                    events.append("LOOKING_AWAY")
                    attention = 60
                
                # Behavior analysis
                behavior = self.behavior_analyzer.analyze(landmarks, frame)
                
                if behavior.get('whispering'):
                    events.append("WHISPERING")
                
                if behavior.get('stress_level', 0) > 60:
                    events.append("STRESS_HIGH")
                
                if behavior.get('reading_pattern'):
                    events.append("READING_PATTERN")
        
        # 3. Object Detection
        objects = []
        detections = self.object_detector.detect(frame)
        
        for det in detections:
            obj_class = det['class_name'].lower()
            objects.append(obj_class)
            
            # Check for cheating objects
            if 'phone' in obj_class or 'cell' in obj_class:
                if det.get('is_partial', False):
                    events.append("PHONE_PARTIAL_DETECTED")
                else:
                    events.append("PHONE_DETECTED")
            
            elif 'tablet' in obj_class or 'ipad' in obj_class:
                events.append("TABLET_DETECTED")
            
            elif 'book' in obj_class or 'paper' in obj_class:
                events.append("SUSPICIOUS_OBJECT")
        
        # 4. Compile results
        return {
            'faces': face_count,
            'gaze': gaze_direction,
            'attention': attention,
            'objects': objects,
            'events': events,
            'detections': {
                'face_boxes': [box.tolist() if hasattr(box, 'tolist') else box for box in faces],
                'object_detections': detections
            }
        }
