"""
Anti-Cheating Interview Monitoring System
Detects suspicious behavior during online interviews
"""
import streamlit as st
import cv2
import numpy as np
import time
from datetime import datetime
import json
import os
from PIL import Image

from utils.face_tracker import FaceTracker
from utils.gaze_estimator import GazeEstimator
from utils.object_detector import ObjectDetector
from utils.id_tracker import PersonTracker


class InterviewMonitor:
    def __init__(self):
        # Initialize components
        if 'initialized' not in st.session_state:
            st.session_state.face_tracker = FaceTracker()
            st.session_state.gaze_estimator = GazeEstimator()
            st.session_state.object_detector = ObjectDetector()
            st.session_state.person_tracker = PersonTracker()
            
            # Monitoring state
            st.session_state.violations = []
            st.session_state.violation_count = 0
            st.session_state.no_face_count = 0
            st.session_state.multiple_face_count = 0
            st.session_state.looking_away_count = 0
            st.session_state.object_detected_count = 0
            st.session_state.last_violation_time = None
            
            # Thresholds
            st.session_state.no_face_threshold = 30  # frames
            st.session_state.looking_away_threshold = 60  # frames
            st.session_state.violation_cooldown = 3  # seconds
            
            # Interview session
            st.session_state.interview_started = False
            st.session_state.interview_start_time = None
            st.session_state.candidate_name = ""
            st.session_state.interview_id = ""
            
            # FPS tracking
            st.session_state.fps = 0
            st.session_state.frame_count = 0
            st.session_state.start_time = time.time()
            
            st.session_state.initialized = True
    
    def log_violation(self, violation_type, description, frame=None):
        """Log a cheating violation"""
        current_time = time.time()
        
        # Cooldown to prevent spam
        if st.session_state.last_violation_time:
            if current_time - st.session_state.last_violation_time < st.session_state.violation_cooldown:
                return
        
        st.session_state.last_violation_time = current_time
        
        violation = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': violation_type,
            'description': description,
            'interview_id': st.session_state.interview_id,
            'candidate': st.session_state.candidate_name
        }
        
        st.session_state.violations.append(violation)
        st.session_state.violation_count += 1
        
        # Save screenshot if frame provided
        if frame is not None:
            os.makedirs('violations', exist_ok=True)
            filename = f"violations/violation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(filename, frame)
            violation['screenshot'] = filename
        
        # Save to log file
        self.save_violations_log()
        
        return violation
    
    def save_violations_log(self):
        """Save violations to JSON file"""
        os.makedirs('violations', exist_ok=True)
        log_file = f"violations/interview_{st.session_state.interview_id}.json"
        
        with open(log_file, 'w') as f:
            json.dump({
                'interview_id': st.session_state.interview_id,
                'candidate': st.session_state.candidate_name,
                'start_time': st.session_state.interview_start_time,
                'violations': st.session_state.violations,
                'total_violations': st.session_state.violation_count
            }, f, indent=2)
    
    def check_cheating(self, frame, face_boxes, gaze_direction, detections):
        """Check for cheating behaviors"""
        violations_detected = []
        
        # Check 1: No face detected
        if len(face_boxes) == 0:
            st.session_state.no_face_count += 1
            if st.session_state.no_face_count > st.session_state.no_face_threshold:
                violation = self.log_violation(
                    "NO_FACE",
                    "Candidate face not visible for extended period",
                    frame
                )
                if violation:
                    violations_detected.append("⚠️ NO FACE DETECTED")
                st.session_state.no_face_count = 0
        else:
            st.session_state.no_face_count = 0
        
        # Check 2: Multiple faces detected
        if len(face_boxes) > 1:
            st.session_state.multiple_face_count += 1
            violation = self.log_violation(
                "MULTIPLE_FACES",
                f"Multiple people detected ({len(face_boxes)} faces)",
                frame
            )
            if violation:
                violations_detected.append(f"🚨 MULTIPLE PEOPLE DETECTED ({len(face_boxes)} faces)")
        else:
            st.session_state.multiple_face_count = 0
        
        # Check 3: Looking away from screen
        if gaze_direction in ["looking_left", "looking_right", "looking_down"]:
            st.session_state.looking_away_count += 1
            if st.session_state.looking_away_count > st.session_state.looking_away_threshold:
                violation = self.log_violation(
                    "LOOKING_AWAY",
                    f"Candidate looking away: {gaze_direction}",
                    frame
                )
                if violation:
                    violations_detected.append(f"👀 LOOKING AWAY: {gaze_direction}")
                st.session_state.looking_away_count = 0
        else:
            st.session_state.looking_away_count = max(0, st.session_state.looking_away_count - 1)
        
        # Check 4: Suspicious objects detected (phone, book, laptop, etc.)
        suspicious_objects = ['cell phone', 'book', 'laptop', 'keyboard', 'mouse', 'tv', 'monitor']
        for det in detections:
            if det['class_name'] in suspicious_objects:
                st.session_state.object_detected_count += 1
                violation = self.log_violation(
                    "SUSPICIOUS_OBJECT",
                    f"Suspicious object detected: {det['class_name']} (confidence: {det['confidence']:.2f})",
                    frame
                )
                if violation:
                    violations_detected.append(f"📱 OBJECT DETECTED: {det['class_name']}")
        
        return violations_detected
    
    def process_frame(self, frame):
        """Process frame and check for violations"""
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
        
        gaze_direction = "unknown"
        
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
            color = (0, 255, 0) if len(face_boxes) == 1 else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
            
            # Draw person ID
            if person_id is not None:
                cv2.putText(frame, f"ID: {person_id}", (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            # Draw landmarks
            st.session_state.face_tracker.draw_landmarks(frame, landmarks)
            
            # Draw head pose
            st.session_state.face_tracker.draw_head_pose(frame, landmarks, head_pose)
            
            # Draw gaze
            st.session_state.gaze_estimator.draw_gaze(frame, landmarks, gaze_vector, gaze_direction)
        
        # Object detection
        detections = st.session_state.object_detector.detect(frame)
        
        if len(detections) > 0:
            st.session_state.object_detector.draw_detections(frame, detections)
        
        # Check for cheating
        violations = self.check_cheating(frame, face_boxes, gaze_direction, detections)
        
        # Draw status
        status_color = (0, 255, 0) if len(violations) == 0 else (0, 0, 255)
        status_text = "MONITORING" if len(violations) == 0 else "VIOLATION DETECTED"
        cv2.putText(frame, status_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 3)
        
        # Draw violation count
        cv2.putText(frame, f"Violations: {st.session_state.violation_count}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Draw FPS
        cv2.putText(frame, f"FPS: {st.session_state.fps:.1f}", (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        return frame, violations


def main():
    st.set_page_config(
        page_title="Interview Anti-Cheating Monitor",
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("🎓 Interview Anti-Cheating Monitoring System")
    st.markdown("Real-time monitoring for online interviews and exams")
    
    # Initialize monitor
    monitor = InterviewMonitor()
    
    # Sidebar - Interview Setup
    st.sidebar.header("📋 Interview Setup")
    
    if not st.session_state.interview_started:
        st.session_state.candidate_name = st.sidebar.text_input(
            "Candidate Name",
            value=st.session_state.candidate_name
        )
        
        st.session_state.interview_id = st.sidebar.text_input(
            "Interview ID",
            value=st.session_state.interview_id or f"INT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if st.sidebar.button("🚀 Start Interview", type="primary"):
            if st.session_state.candidate_name and st.session_state.interview_id:
                st.session_state.interview_started = True
                st.session_state.interview_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.rerun()
            else:
                st.sidebar.error("Please enter candidate name and interview ID")
    else:
        st.sidebar.success(f"✅ Interview Active")
        st.sidebar.info(f"**Candidate:** {st.session_state.candidate_name}")
        st.sidebar.info(f"**ID:** {st.session_state.interview_id}")
        st.sidebar.info(f"**Started:** {st.session_state.interview_start_time}")
        
        if st.sidebar.button("🛑 End Interview", type="secondary"):
            st.session_state.interview_started = False
            monitor.save_violations_log()
            st.rerun()
    
    # Sidebar - Monitoring Settings
    st.sidebar.header("⚙️ Settings")
    
    st.session_state.no_face_threshold = st.sidebar.slider(
        "No Face Alert (frames)",
        10, 100, st.session_state.no_face_threshold
    )
    
    st.session_state.looking_away_threshold = st.sidebar.slider(
        "Looking Away Alert (frames)",
        30, 120, st.session_state.looking_away_threshold
    )
    
    # Sidebar - Statistics
    st.sidebar.header("📊 Statistics")
    st.sidebar.metric("Total Violations", st.session_state.violation_count)
    st.sidebar.metric("No Face Incidents", len([v for v in st.session_state.violations if v['type'] == 'NO_FACE']))
    st.sidebar.metric("Multiple People", len([v for v in st.session_state.violations if v['type'] == 'MULTIPLE_FACES']))
    st.sidebar.metric("Looking Away", len([v for v in st.session_state.violations if v['type'] == 'LOOKING_AWAY']))
    st.sidebar.metric("Objects Detected", len([v for v in st.session_state.violations if v['type'] == 'SUSPICIOUS_OBJECT']))
    
    # Main content
    if not st.session_state.interview_started:
        st.info("👆 Please enter candidate details and click 'Start Interview' to begin monitoring")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### ✅ Monitored Behaviors")
            st.markdown("""
            - Face visibility
            - Multiple people detection
            - Gaze direction tracking
            - Suspicious object detection
            """)
        
        with col2:
            st.markdown("### 🚨 Violation Types")
            st.markdown("""
            - **NO_FACE**: Face not visible
            - **MULTIPLE_FACES**: Multiple people
            - **LOOKING_AWAY**: Not looking at screen
            - **SUSPICIOUS_OBJECT**: Phone, book, etc.
            """)
        
        with col3:
            st.markdown("### 📝 Features")
            st.markdown("""
            - Real-time monitoring
            - Automatic violation logging
            - Screenshot capture
            - Detailed reports
            """)
    
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📹 Live Monitoring")
            video_placeholder = st.empty()
            alert_placeholder = st.empty()
        
        with col2:
            st.subheader("⚠️ Recent Violations")
            violations_placeholder = st.empty()
        
        # Camera processing
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        try:
            while st.session_state.interview_started:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to read from camera")
                    break
                
                # Process frame
                processed_frame, violations = monitor.process_frame(frame)
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                
                # Display
                video_placeholder.image(rgb_frame, channels="RGB", width="stretch")
                
                # Show alerts
                if violations:
                    alert_placeholder.error("\n\n".join(violations))
                else:
                    alert_placeholder.success("✅ No violations detected")
                
                # Show recent violations
                with violations_placeholder.container():
                    if st.session_state.violations:
                        recent = st.session_state.violations[-10:][::-1]
                        for v in recent:
                            with st.expander(f"{v['type']} - {v['timestamp']}", expanded=False):
                                st.write(f"**Description:** {v['description']}")
                                if 'screenshot' in v:
                                    st.write(f"**Screenshot:** {v['screenshot']}")
                    else:
                        st.info("No violations recorded yet")
                
                # Small delay
                time.sleep(0.03)
        
        finally:
            cap.release()


if __name__ == "__main__":
    main()
