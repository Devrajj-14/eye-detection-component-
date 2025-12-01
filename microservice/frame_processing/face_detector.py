"""
Face Detection Module
Uses dlib for face detection and landmark extraction
"""
import cv2
import dlib
import numpy as np
from typing import List, Optional, Tuple
import asyncio


class FaceDetector:
    """Face detection and landmark extraction"""
    
    def __init__(self):
        self.detector = None
        self.predictor = None
    
    async def load_models(self):
        """Load face detection models"""
        # Use dlib's HOG-based detector
        self.detector = dlib.get_frontal_face_detector()
        
        # Load shape predictor (68 landmarks)
        try:
            self.predictor = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")
        except:
            print("⚠️ Warning: shape_predictor not found, using basic detection only")
            self.predictor = None
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in frame
        
        Args:
            frame: BGR image
        
        Returns:
            List of face bounding boxes (x, y, w, h)
        """
        if self.detector is None:
            return []
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.detector(gray, 1)
        
        # Convert to (x, y, w, h) format
        face_boxes = []
        for face in faces:
            x = face.left()
            y = face.top()
            w = face.width()
            h = face.height()
            face_boxes.append((x, y, w, h))
        
        return face_boxes
    
    def get_landmarks(self, frame: np.ndarray, face_box: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        Get facial landmarks for a face
        
        Args:
            frame: BGR image
            face_box: Face bounding box (x, y, w, h)
        
        Returns:
            Numpy array of landmarks (68, 2) or None
        """
        if self.predictor is None:
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Convert box to dlib rectangle
        x, y, w, h = face_box
        rect = dlib.rectangle(x, y, x + w, y + h)
        
        # Get landmarks
        shape = self.predictor(gray, rect)
        
        # Convert to numpy array
        landmarks = np.array([[p.x, p.y] for p in shape.parts()])
        
        return landmarks
    
    def get_head_pose(self, landmarks: np.ndarray, frame_shape: Tuple) -> Tuple[float, float, float]:
        """
        Estimate head pose from landmarks
        
        Args:
            landmarks: Facial landmarks (68, 2)
            frame_shape: Frame shape (h, w, c)
        
        Returns:
            (pitch, yaw, roll) in degrees
        """
        # 3D model points
        model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ])
        
        # 2D image points from landmarks
        image_points = np.array([
            landmarks[30],    # Nose tip
            landmarks[8],     # Chin
            landmarks[36],    # Left eye left corner
            landmarks[45],    # Right eye right corner
            landmarks[48],    # Left mouth corner
            landmarks[54]     # Right mouth corner
        ], dtype="double")
        
        # Camera internals
        h, w = frame_shape[:2]
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")
        
        dist_coeffs = np.zeros((4, 1))
        
        # Solve PnP
        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        # Convert rotation vector to euler angles
        rotation_mat, _ = cv2.Rodrigues(rotation_vector)
        pose_mat = cv2.hconcat((rotation_mat, translation_vector))
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(pose_mat)
        
        pitch = euler_angles[0][0]
        yaw = euler_angles[1][0]
        roll = euler_angles[2][0]
        
        return (pitch, yaw, roll)
