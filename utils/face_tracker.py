"""
OpenFace 3.0 compatible face detection and landmark extraction
"""
import cv2
import dlib
import numpy as np


class FaceTracker:
    def __init__(self, model_path="models/shape_predictor_68_face_landmarks.dat"):
        """Initialize face detector and landmark predictor"""
        self.detector = dlib.get_frontal_face_detector()
        try:
            self.predictor = dlib.shape_predictor(model_path)
        except:
            print(f"Warning: Could not load {model_path}")
            print("Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
            self.predictor = None
    
    def detect_faces(self, frame):
        """
        Detect all faces in frame
        Returns: list of (x, y, w, h) bounding boxes
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray, 0)
        
        boxes = []
        for face in faces:
            x = face.left()
            y = face.top()
            w = face.right() - x
            h = face.bottom() - y
            boxes.append((x, y, w, h))
        
        return boxes
    
    def get_landmarks(self, frame, box):
        """
        Extract 68 facial landmarks for given face box
        Returns: numpy array of shape (68, 2)
        """
        if self.predictor is None:
            return None
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        x, y, w, h = box
        rect = dlib.rectangle(x, y, x + w, y + h)
        
        shape = self.predictor(gray, rect)
        landmarks = np.zeros((68, 2), dtype=int)
        
        for i in range(68):
            landmarks[i] = (shape.part(i).x, shape.part(i).y)
        
        return landmarks
    
    def get_head_pose(self, landmarks, frame_shape):
        """
        Estimate head pose from landmarks
        Returns: (pitch, yaw, roll) in degrees
        """
        if landmarks is None or len(landmarks) < 68:
            return (0, 0, 0)
        
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
        success, rotation_vec, translation_vec = cv2.solvePnP(
            model_points, image_points, camera_matrix, dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if not success:
            return (0, 0, 0)
        
        # Convert rotation vector to Euler angles
        rotation_mat, _ = cv2.Rodrigues(rotation_vec)
        pose_mat = cv2.hconcat((rotation_mat, translation_vec))
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(pose_mat)
        
        pitch, yaw, roll = euler_angles.flatten()[:3]
        
        return (pitch, yaw, roll)
    
    def draw_landmarks(self, frame, landmarks, color=(0, 255, 0)):
        """Draw 68 facial landmarks on frame"""
        if landmarks is None:
            return
        
        for (x, y) in landmarks:
            cv2.circle(frame, (x, y), 1, color, -1)
    
    def draw_head_pose(self, frame, landmarks, pose):
        """Draw head pose axes on frame"""
        if landmarks is None or len(landmarks) < 68:
            return
        
        pitch, yaw, roll = pose
        
        # Get nose tip as origin
        nose_tip = tuple(landmarks[30])
        
        # Draw axes
        length = 100
        
        # X-axis (red) - pitch
        end_x = int(nose_tip[0] + length * np.sin(np.radians(yaw)))
        end_y = int(nose_tip[1] - length * np.sin(np.radians(pitch)))
        cv2.line(frame, nose_tip, (end_x, end_y), (0, 0, 255), 2)
        
        # Y-axis (green) - yaw
        end_x = int(nose_tip[0] + length * np.cos(np.radians(yaw)))
        end_y = int(nose_tip[1])
        cv2.line(frame, nose_tip, (end_x, end_y), (0, 255, 0), 2)
        
        # Z-axis (blue) - roll
        cv2.line(frame, nose_tip, 
                (nose_tip[0], nose_tip[1] + int(length * np.cos(np.radians(roll)))),
                (255, 0, 0), 2)
