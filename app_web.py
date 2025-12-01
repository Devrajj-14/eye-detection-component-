"""
Streamlit web interface for OpenFace application
"""
import streamlit as st
import cv2
import numpy as np
import time
from PIL import Image
import threading
import queue

from utils.face_tracker import FaceTracker
from utils.gaze_estimator import GazeEstimator
from utils.calibration import GazeCalibration
from utils.object_detector import ObjectDetector
from utils.id_tracker import PersonTracker


class WebApp:
    def __init__(self):
        # Initialize components
        if 'initialized' not in st.session_state:
            st.session_state.face_tracker = FaceTracker()
            st.session_state.gaze_estimator = GazeEstimator()
            st.session_state.calibration = GazeCalibration()
            st.session_state.object_detector = ObjectDetector()
            st.session_state.person_tracker = PersonTracker()
            
            # State
            st.session_state.detection_enabled = False
            st.session_state.calibrating = False
            st.session_state.fps = 0
            st.session_state.frame_count = 0
            st.session_state.start_time = time.time()
            st.session_state.calibration_start_time = None
            st.session_state.calibration_sample_duration = 1.0
            st.session_state.initialized = True
            st.session_state.camera_running = False
    
    def process_frame(self, frame):
        """Process a single frame"""
        st.session_state.frame_count += 1
        
        # Calculate FPS
        elapsed = time.time() - st.session_state.start_time
        if elapsed > 1.0:
            st.session_state.fps = st.session_state.frame_count / elapsed
            st.session_state.frame_count = 0
            st.session_state.start_time = time.time()
        
        # Detect faces
        face_boxes = st.session_state.face_tracker.detect_faces(frame)
        tracked_objects = st.session_state.person_tracker.update(face_boxes)
        
        # Process each face
        for box in face_boxes:
            person_id = st.session_state.person_tracker.get_id_for_box(box)
            landmarks = st.session_state.face_tracker.get_landmarks(frame, box)
            head_pose = st.session_state.face_tracker.get_head_pose(landmarks, frame.shape)
            gaze_vector, gaze_direction = st.session_state.gaze_estimator.estimate_gaze(
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
            st.session_state.face_tracker.draw_landmarks(frame, landmarks)
            
            # Draw head pose
            st.session_state.face_tracker.draw_head_pose(frame, landmarks, head_pose)
            
            # Draw gaze
            st.session_state.gaze_estimator.draw_gaze(frame, landmarks, gaze_vector, gaze_direction)
            
            # Handle calibration
            if st.session_state.calibrating and landmarks is not None:
                if st.session_state.calibration_start_time is None:
                    st.session_state.calibration_start_time = time.time()
                
                elapsed = time.time() - st.session_state.calibration_start_time
                if elapsed >= st.session_state.calibration_sample_duration:
                    # Extract eye features
                    left_eye_region, left_box = st.session_state.gaze_estimator.get_eye_region(
                        frame, landmarks, st.session_state.gaze_estimator.LEFT_EYE
                    )
                    right_eye_region, right_box = st.session_state.gaze_estimator.get_eye_region(
                        frame, landmarks, st.session_state.gaze_estimator.RIGHT_EYE
                    )
                    
                    left_iris = st.session_state.gaze_estimator.get_iris_center(left_eye_region)
                    right_iris = st.session_state.gaze_estimator.get_iris_center(right_eye_region)
                    
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
                    
                    complete = st.session_state.calibration.add_calibration_sample(eye_features)
                    st.session_state.calibration_start_time = None
                    
                    if complete:
                        st.session_state.calibrating = False
        
        # Draw calibration point if active
        if st.session_state.calibrating:
            st.session_state.calibration.draw_calibration_point(frame)
        
        # Object detection
        if st.session_state.detection_enabled:
            detections = st.session_state.object_detector.detect(frame)
            
            if len(detections) > 0:
                st.session_state.object_detector.draw_detections(frame, detections)
                st.session_state.object_detector.save_detection(frame, detections)
        
        # Draw FPS
        cv2.putText(frame, f"FPS: {st.session_state.fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Draw people count
        cv2.putText(frame, f"People: {len(face_boxes)}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame


def main():
    st.set_page_config(
        page_title="OpenFace 3.0 Multi-Person Tracker",
        page_icon="👁️",
        layout="wide"
    )
    
    st.title("👁️ OpenFace 3.0 Multi-Person Tracker")
    st.markdown("Real-time face tracking, eye gaze estimation, and object detection")
    
    # Initialize app
    app = WebApp()
    
    # Sidebar controls
    st.sidebar.header("Controls")
    
    # Camera control
    camera_on = st.sidebar.checkbox("Start Camera", value=False)
    
    # Calibration control
    if st.sidebar.button("Start Calibration"):
        st.session_state.calibration.start_calibration()
        st.session_state.calibrating = True
        st.session_state.calibration_start_time = None
    
    if st.sidebar.button("Stop Calibration"):
        st.session_state.calibrating = False
    
    # Detection control
    st.session_state.detection_enabled = st.sidebar.checkbox(
        "Enable Object Detection",
        value=st.session_state.detection_enabled
    )
    
    # Status display
    st.sidebar.header("Status")
    
    if st.session_state.calibrating:
        point = st.session_state.calibration.current_point_idx + 1
        total = len(st.session_state.calibration.calibration_points)
        st.sidebar.info(f"📍 Calibrating: {point}/{total}")
    elif st.session_state.calibration.model_x is not None:
        st.sidebar.success("✅ Calibration Complete")
    
    if st.session_state.detection_enabled:
        st.sidebar.info("🔍 Object Detection: ON")
    
    st.sidebar.metric("FPS", f"{st.session_state.fps:.1f}")
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Live Video Feed")
        video_placeholder = st.empty()
    
    with col2:
        st.subheader("Information")
        st.markdown("""
        **Features:**
        - 👥 Multi-person tracking
        - 👁️ Eye gaze estimation
        - 📍 9-point calibration
        - 🔍 Object detection
        - 🆔 Person ID tracking
        
        **Instructions:**
        1. Click "Start Camera"
        2. Click "Start Calibration"
        3. Look at red dots
        4. Enable detection if needed
        """)
        
        # Statistics
        st.subheader("Statistics")
        stats_placeholder = st.empty()
    
    # Camera processing
    if camera_on:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        try:
            while camera_on:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to read from camera")
                    break
                
                # Process frame
                processed_frame = app.process_frame(frame)
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                
                # Display
                video_placeholder.image(rgb_frame, channels="RGB", width="stretch")
                
                # Update stats
                face_boxes = st.session_state.face_tracker.detect_faces(frame)
                with stats_placeholder.container():
                    st.metric("People Detected", len(face_boxes))
                    st.metric("FPS", f"{st.session_state.fps:.1f}")
                
                # Small delay
                time.sleep(0.03)
        
        finally:
            cap.release()
    else:
        video_placeholder.info("👆 Click 'Start Camera' in the sidebar to begin")


if __name__ == "__main__":
    main()
