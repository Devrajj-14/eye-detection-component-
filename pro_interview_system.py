"""
Professional Anti-Cheating Interview System
Ultra-smooth UX with comprehensive monitoring
"""
import streamlit as st
import cv2
import numpy as np
import time
from datetime import datetime
import json
import os
from collections import deque

from utils.face_tracker import FaceTracker
from utils.gaze_estimator import GazeEstimator
from utils.object_detector import ObjectDetector
from utils.id_tracker import PersonTracker
from utils.behavior_analyzer import BehaviorAnalyzer
from utils.audio_monitor import AudioMonitor
from utils.environment_monitor import EnvironmentMonitor
from utils.smart_detector import SmartDetector
from utils.risk_model import FrameAnalysis, update_risk, get_risk_level, get_status_message


# Page config
st.set_page_config(
    page_title="AI Interview Integrity System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ultra-smooth UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .status-clean {
        background-color: #10b981;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        text-align: center;
    }
    .status-suspicious {
        background-color: #f59e0b;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        text-align: center;
    }
    .status-cheating {
        background-color: #ef4444;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        text-align: center;
    }
    .metric-card {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }
    .violation-alert {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


class ProInterviewSystem:
    def __init__(self):
        if 'initialized' not in st.session_state:
            # Core components
            st.session_state.face_tracker = FaceTracker()
            st.session_state.gaze_estimator = GazeEstimator()
            st.session_state.object_detector = ObjectDetector()
            st.session_state.person_tracker = PersonTracker()
            st.session_state.behavior_analyzer = BehaviorAnalyzer()
            st.session_state.audio_monitor = AudioMonitor()
            st.session_state.environment_monitor = EnvironmentMonitor()
            st.session_state.smart_detector = SmartDetector()
            
            # Session state
            st.session_state.interview_active = False
            st.session_state.interview_phase = "setup"  # setup, verification, active, completed
            st.session_state.candidate_name = ""
            st.session_state.interview_id = ""
            st.session_state.start_time = None
            st.session_state.end_time = None
            
            # Risk scoring - SINGLE SOURCE OF TRUTH
            st.session_state.risk_score = 0  # Start at 0, not 100!
            st.session_state.status = "CLEAN"
            st.session_state.prev_time = time.time()
            
            # Monitoring data
            st.session_state.gaze_history = deque(maxlen=100)
            st.session_state.violations_log = []
            st.session_state.fps = 0
            st.session_state.frame_count = 0
            st.session_state.fps_start_time = time.time()
            
            # Counters
            st.session_state.no_face_frames = 0
            st.session_state.looking_away_frames = 0
            st.session_state.phone_detections = 0
            st.session_state.multiple_face_detections = 0
            
            # Attention tracking
            st.session_state.attention_scores = []
            st.session_state.stress_scores = []
            
            st.session_state.initialized = True
    
    def log_violation(self, violation_type, description, severity, frame=None):
        """Log violation with screenshot"""
        violation = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            'type': violation_type,
            'description': description,
            'severity': severity
        }
        
        # Save screenshot
        if frame is not None:
            os.makedirs('evidence', exist_ok=True)
            filename = f"evidence/{st.session_state.interview_id}_{violation_type}_{datetime.now().strftime('%H%M%S')}.jpg"
            cv2.imwrite(filename, frame)
            violation['screenshot'] = filename
        
        st.session_state.violations_log.append(violation)
        
        return violation
    
    def save_calibration(self):
        """Save calibration data"""
        if len(st.session_state.calibration_samples) < 9:
            return False
        
        # Extract gaze values
        gaze_x_values = [s['gaze_x'] for s in st.session_state.calibration_samples]
        gaze_y_values = [s['gaze_y'] for s in st.session_state.calibration_samples]
        
        # Compute boundaries with margin
        margin = 0.3
        gaze_x_range = max(gaze_x_values) - min(gaze_x_values)
        gaze_y_range = max(gaze_y_values) - min(gaze_y_values)
        
        screen_bounds = {
            'gaze_x_min': min(gaze_x_values) - gaze_x_range * margin,
            'gaze_x_max': max(gaze_x_values) + gaze_x_range * margin,
            'gaze_y_min': min(gaze_y_values) - gaze_y_range * margin,
            'gaze_y_max': max(gaze_y_values) + gaze_y_range * margin,
        }
        
        # Save to gaze estimator
        st.session_state.gaze_estimator.screen_bounds = screen_bounds
        st.session_state.gaze_estimator.is_calibrated = True
        
        # Save to file
        os.makedirs('calibration', exist_ok=True)
        with open('calibration/calibration_data.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'screen_bounds': screen_bounds,
                'num_samples': len(st.session_state.calibration_samples)
            }, f, indent=2)
        
        return True
    
    def process_frame(self, frame):
        """Comprehensive frame processing with clean risk scoring"""
        # FPS calculation
        st.session_state.frame_count += 1
        elapsed = time.time() - st.session_state.fps_start_time
        if elapsed > 1.0:
            st.session_state.fps = st.session_state.frame_count / elapsed
            st.session_state.frame_count = 0
            st.session_state.fps_start_time = time.time()
        
        # Time delta for risk decay
        now = time.time()
        dt = now - st.session_state.prev_time
        st.session_state.prev_time = now
        
        # Collect cheating events for this frame
        cheating_events = []
        warnings = []
        violations_this_frame = []
        
        # 1. Face Detection
        face_boxes = st.session_state.face_tracker.detect_faces(frame)
        tracked_objects = st.session_state.person_tracker.update(face_boxes)
        
        # 2. Check face count - Use SMART detection
        multiple_people, face_count = st.session_state.smart_detector.detect_multiple_people(face_boxes)
        
        if len(face_boxes) == 0:
            st.session_state.no_face_frames += 1
            if st.session_state.no_face_frames > 90:  # 3 seconds at 30fps
                cheating_events.append("NO_FACE")
                warnings.append("⚠️ No face detected for 3+ seconds")
                violation = self.log_violation(
                    "NO_FACE",
                    "Candidate face not visible for extended period",
                    "high",
                    frame
                )
                violations_this_frame.append(violation)
                st.session_state.no_face_frames = 0
        else:
            st.session_state.no_face_frames = 0
        
        # Only flag if CONSISTENTLY multiple faces (not single frame)
        if multiple_people:
            st.session_state.multiple_face_detections += 1
            cheating_events.append("SECOND_PERSON")
            warnings.append(f"🚨 Multiple people detected ({face_count} faces)")
            violation = self.log_violation(
                "MULTIPLE_FACES",
                f"Multiple people detected ({face_count} faces)",
                "critical",
                frame
            )
            violations_this_frame.append(violation)
        
        # 3. Process each face
        gaze_direction = "unknown"
        stress_level = 0
        
        for idx, box in enumerate(face_boxes):
            person_id = st.session_state.person_tracker.get_id_for_box(box)
            landmarks = st.session_state.face_tracker.get_landmarks(frame, box)
            
            if landmarks is not None:
                # Head pose
                head_pose = st.session_state.face_tracker.get_head_pose(landmarks, frame.shape)
                
                # Gaze estimation (now returns gaze_x, gaze_y for calibration)
                gaze_result = st.session_state.gaze_estimator.estimate_gaze(
                    frame, landmarks, head_pose
                )
                
                # Handle both old and new return formats
                if len(gaze_result) == 4:
                    gaze_vector, gaze_direction, gaze_x, gaze_y = gaze_result
                else:
                    gaze_vector, gaze_direction = gaze_result
                    gaze_x, gaze_y = 0, 0
                
                st.session_state.gaze_history.append(gaze_direction)
                
                # Debug: Print gaze direction every 30 frames
                if st.session_state.frame_count % 30 == 0:
                    print(f"👁️ Gaze: {gaze_direction} | Calibrated: {st.session_state.gaze_estimator.is_calibrated}")
                
                # Behavior analysis
                st.session_state.behavior_analyzer.detect_blink(landmarks)
                stress_level = st.session_state.behavior_analyzer.analyze_stress_level(landmarks, head_pose)
                st.session_state.stress_scores.append(stress_level)
                
                # High stress indicator
                if stress_level > 60:
                    cheating_events.append("STRESS_HIGH")
                
                # Whispering detection
                if st.session_state.behavior_analyzer.detect_whispering(landmarks):
                    cheating_events.append("WHISPERING")
                    warnings.append("⚠️ Potential whispering detected")
                    violation = self.log_violation(
                        "WHISPERING",
                        "Potential whispering detected",
                        "medium",
                        frame
                    )
                    violations_this_frame.append(violation)
                
                # Reading pattern
                if st.session_state.behavior_analyzer.detect_reading_pattern(st.session_state.gaze_history):
                    cheating_events.append("READING_PATTERN")
                    warnings.append("⚠️ Reading pattern detected")
                    violation = self.log_violation(
                        "READING_PATTERN",
                        "Reading pattern detected (left-right scanning)",
                        "high",
                        frame
                    )
                    violations_this_frame.append(violation)
                
                # Draw visualizations
                x, y, w, h = box
                color = (0, 255, 0) if len(face_boxes) == 1 else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
                
                if person_id is not None:
                    cv2.putText(frame, f"ID: {person_id}", (x, y - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                
                st.session_state.face_tracker.draw_landmarks(frame, landmarks)
                st.session_state.face_tracker.draw_head_pose(frame, landmarks, head_pose)
                st.session_state.gaze_estimator.draw_gaze(frame, landmarks, gaze_vector, gaze_direction)
        
        # 4. Gaze monitoring - CALIBRATION-BASED SCREEN BOUNDARY DETECTION
        if len(face_boxes) > 0 and gaze_direction != "unknown":
            # Check if gaze estimator has calibration
            if hasattr(st.session_state.gaze_estimator, 'is_calibrated') and st.session_state.gaze_estimator.is_calibrated:
                # CALIBRATED MODE: Only trigger if eyes go BEYOND screen matrix
                # The gaze_direction is already set by calibration boundaries
                # "looking_center" = within screen matrix (OK)
                # Any other direction = beyond screen matrix (CHEATING)
                
                if gaze_direction != "looking_center":
                    st.session_state.looking_away_frames += 1
                    
                    # Show counter for debugging
                    if st.session_state.looking_away_frames % 5 == 0:
                        print(f"⚠️ Looking away: {gaze_direction} - Frame {st.session_state.looking_away_frames}/25")
                    
                    if st.session_state.looking_away_frames > 25:  # ~0.8 seconds at 30fps
                        cheating_events.append("EYES_BEYOND_SCREEN")
                        warnings.append(f"🚨 Eyes beyond screen boundary: {gaze_direction}")
                        print(f"🚨 ALERT TRIGGERED: Eyes beyond screen - {gaze_direction}")
                        violation = self.log_violation(
                            "EYES_BEYOND_SCREEN",
                            f"Eyes went beyond calibrated screen boundary: {gaze_direction}",
                            "high",
                            frame
                        )
                        violations_this_frame.append(violation)
                        st.session_state.looking_away_frames = 0
                else:
                    # Eyes within screen matrix - reset counter
                    st.session_state.looking_away_frames = 0
            else:
                # UNCALIBRATED MODE: Use fallback detection
                # Recommend running calibration for better accuracy
                if gaze_direction in ["looking_left", "looking_right", "looking_down", "looking_up"]:
                    st.session_state.looking_away_frames += 1
                    
                    # Show counter for debugging
                    if st.session_state.looking_away_frames % 5 == 0:
                        print(f"⚠️ Looking away (uncalibrated): {gaze_direction} - Frame {st.session_state.looking_away_frames}/25")
                    
                    if st.session_state.looking_away_frames > 25:  # ~0.8 seconds without calibration
                        cheating_events.append("LOOKING_AWAY_UNCALIBRATED")
                        warnings.append(f"⚠️ Looking away: {gaze_direction} (Run calibration for better accuracy)")
                        print(f"🚨 ALERT TRIGGERED: Looking away - {gaze_direction}")
                        violation = self.log_violation(
                            "LOOKING_AWAY_UNCALIBRATED",
                            f"Looking away: {gaze_direction} (System not calibrated)",
                            "high",
                            frame
                        )
                        violations_this_frame.append(violation)
                        st.session_state.looking_away_frames = 0
                else:
                    st.session_state.looking_away_frames = 0
        else:
            st.session_state.looking_away_frames = 0
        
        # Calculate attention score - Use SMART calculation
        attention_score = st.session_state.smart_detector.calculate_attention_score(st.session_state.gaze_history)
        st.session_state.attention_scores.append(attention_score)
        
        # 5. Object Detection - VERY SENSITIVE, run every frame
        all_detections = st.session_state.object_detector.detect(frame)
        
        # STRICT filtering - only real cheating objects
        first_face_box = face_boxes[0] if len(face_boxes) > 0 else None
        filtered_detections = st.session_state.smart_detector.filter_yolo_detections(
            all_detections,
            first_face_box
        )
        
        # INSTANT detection - process ALL filtered detections immediately
        for det in filtered_detections:
            obj_class = det['class_name'].lower()
            
            # INSTANT trigger - no consecutive frame requirement
            st.session_state.phone_detections += 1
            
            if 'phone' in obj_class or 'mobile' in obj_class or 'cell' in obj_class:
                cheating_events.append("PHONE_DETECTED")
                warnings.append(f"📱 PHONE DETECTED (confidence: {det['confidence']:.2f})")
            elif 'book' in obj_class or 'paper' in obj_class or 'notebook' in obj_class:
                cheating_events.append("BOOK_PAPER")
                warnings.append(f"📖 Book/Paper detected (confidence: {det['confidence']:.2f})")
            elif 'tablet' in obj_class or 'ipad' in obj_class:
                cheating_events.append("TABLET_DETECTED")
                warnings.append(f"📱 Tablet detected (confidence: {det['confidence']:.2f})")
            elif 'laptop' in obj_class or 'computer' in obj_class:
                cheating_events.append("LAPTOP_DETECTED")
                warnings.append(f"💻 Laptop detected (confidence: {det['confidence']:.2f})")
            else:
                cheating_events.append("SUSPICIOUS_OBJECT")
                warnings.append(f"⚠️ {obj_class} detected (confidence: {det['confidence']:.2f})")
            
            violation = self.log_violation(
                "PHONE_DETECTED" if 'phone' in obj_class else "SUSPICIOUS_OBJECT",
                f"Object: {det['class_name']} (confidence: {det['confidence']:.2f})",
                "critical",
                frame
            )
            violations_this_frame.append(violation)
        
        # Draw only filtered detections
        if len(filtered_detections) > 0:
            st.session_state.object_detector.draw_detections(frame, filtered_detections)
        
        # 6. Environment monitoring - DISABLED to reduce false positives
        # Only enable if you need background/reflection detection
        # env_events = st.session_state.environment_monitor.analyze_frame(
        #     frame,
        #     face_boxes[0] if len(face_boxes) > 0 else None
        # )
        # 
        # for event in env_events:
        #     # Only add if severity is high
        #     if event['severity'] == 'high':
        #         cheating_events.append(event['type'])
        #         warnings.append(f"⚠️ {event['description']}")
        #         violation = self.log_violation(
        #             event['type'],
        #             event['description'],
        #             event['severity'],
        #             frame
        #         )
        #         violations_this_frame.append(violation)
        
        # 7. Update risk score using clean model
        frame_analysis = FrameAnalysis(
            cheating_events=cheating_events,
            attention_score=attention_score / 100.0,  # Convert to 0-1
            warnings=warnings,
            stress_level=stress_level
        )
        
        # Update global risk score - SINGLE SOURCE OF TRUTH
        st.session_state.risk_score = update_risk(
            st.session_state.risk_score,
            frame_analysis,
            dt
        )
        
        # Update status based on risk
        risk_level, color_name = get_risk_level(st.session_state.risk_score)
        st.session_state.status = risk_level
        
        # 8. Draw status overlay
        status_color = (0, 255, 0) if risk_level == "CLEAN" else (0, 165, 255) if risk_level == "SUSPICIOUS" else (0, 0, 255)
        
        cv2.putText(frame, f"STATUS: {risk_level}", (10, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, status_color, 3)
        
        cv2.putText(frame, f"Risk Score: {st.session_state.risk_score:.0f}/100", (10, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
        
        cv2.putText(frame, f"FPS: {st.session_state.fps:.1f}", (10, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Attention: {attention_score:.0f}%", (10, 160),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Show looking away counter if active
        if st.session_state.looking_away_frames > 0:
            counter_text = f"Looking Away: {st.session_state.looking_away_frames}/25"
            counter_color = (0, 165, 255) if st.session_state.looking_away_frames < 15 else (0, 0, 255)
            cv2.putText(frame, counter_text, (10, 200),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, counter_color, 2)
        
        return frame, violations_this_frame, warnings


def main():
    system = ProInterviewSystem()
    
    # Header
    st.markdown('<h1 class="main-header">🎯 AI Interview Integrity System</h1>', unsafe_allow_html=True)
    st.markdown("**Professional Anti-Cheating Monitoring with Real-time Analysis**")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Interview Control")
        
        if st.session_state.interview_phase == "setup":
            st.subheader("Setup Interview")
            
            st.session_state.candidate_name = st.text_input("Candidate Name", value=st.session_state.candidate_name)
            st.session_state.interview_id = st.text_input(
                "Interview ID",
                value=st.session_state.interview_id or f"INT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            if st.button("🚀 Start Interview", type="primary", use_container_width=True):
                if st.session_state.candidate_name and st.session_state.interview_id:
                    st.session_state.interview_phase = "active"
                    st.session_state.interview_active = True
                    st.session_state.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.rerun()
                else:
                    st.error("Please fill all fields")
        

        
        elif st.session_state.interview_phase == "active":
            st.success("✅ Interview Active")
            st.info(f"**Candidate:** {st.session_state.candidate_name}")
            st.info(f"**ID:** {st.session_state.interview_id}")
            st.info(f"**Started:** {st.session_state.start_time}")
            
            if st.button("🛑 End Interview", type="secondary", use_container_width=True):
                st.session_state.interview_phase = "completed"
                st.session_state.interview_active = False
                st.session_state.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.rerun()
        
        st.divider()
        
        st.divider()
        
        # Real-time metrics - SINGLE SOURCE OF TRUTH
        st.header("📊 Live Metrics")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Risk Score", f"{st.session_state.risk_score:.0f}/100")
        with col2:
            st.metric("Status", st.session_state.status)
        
        st.metric("Total Violations", len(st.session_state.violations_log))
        st.metric("Phone Detections", st.session_state.phone_detections)
        st.metric("Multiple Faces", st.session_state.multiple_face_detections)
        
        if len(st.session_state.gaze_history) > 0:
            attention = st.session_state.behavior_analyzer.calculate_attention_score(st.session_state.gaze_history)
            st.metric("Attention", f"{attention:.0f}%")
    
    # Main content
    if st.session_state.interview_phase == "setup":
        st.info("👆 Please enter interview details in the sidebar to begin")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### ✅ Comprehensive Monitoring")
            st.markdown("""
            - 👤 Face & Identity Verification
            - 👁️ Eye Gaze Tracking
            - 🎭 Behavior Analysis
            - 📱 Object Detection
            - 🌍 Environment Monitoring
            - 🔊 Audio Analysis
            """)
        
        with col2:
            st.markdown("### 🚨 Detected Violations")
            st.markdown("""
            - Multiple people
            - Phone/Device usage
            - Looking away repeatedly
            - Whispering
            - Background changes
            - Suspicious objects
            """)
        
        with col3:
            st.markdown("### 📊 Integrity Report")
            st.markdown("""
            - Risk score (0-100)
            - Attention analysis
            - Behavior summary
            - Evidence screenshots
            - Detailed timeline
            - Final verdict
            """)
    
    elif st.session_state.interview_phase == "active":
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📹 Live Monitoring")
            video_placeholder = st.empty()
        
        with col2:
            st.subheader("⚠️ Recent Violations")
            violations_placeholder = st.empty()
        
        # Camera processing with proper loop
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            st.error("❌ Camera not accessible")
            st.info("💡 Camera test passed but Streamlit can't access it. Try running: `python test_camera_simple.py`")
            st.stop()
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Process frames in a loop
        try:
            frame_count = 0
            while st.session_state.interview_active and frame_count < 100:  # Process 100 frames then rerun
                ret, frame = cap.read()
                if not ret:
                    st.warning("⚠️ Camera frame dropped")
                    time.sleep(0.1)
                    continue
                
                # Process frame
                processed_frame, violations, warnings = system.process_frame(frame)
                
                # Display
                rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(rgb_frame, channels="RGB", width="stretch")
                
                # Show violations and warnings
                with violations_placeholder.container():
                    # Show current warnings
                    if warnings:
                        for warning in warnings:
                            st.warning(warning)
                    
                    # Show recent violations
                    if st.session_state.violations_log:
                        st.markdown("**Recent Violations:**")
                        recent = st.session_state.violations_log[-5:][::-1]
                        for v in recent:
                            severity_emoji = "🚨" if v['severity'] == "critical" else "⚠️" if v['severity'] == "high" else "ℹ️"
                            st.markdown(f"""
                            <div class="violation-alert">
                                {severity_emoji} <strong>{v['type']}</strong><br>
                                {v['description']}<br>
                                <small>{v['timestamp']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("✅ No violations detected")
                
                time.sleep(0.03)
                frame_count += 1
        
        finally:
            cap.release()
        
        # Rerun to continue processing
        if st.session_state.interview_active:
            st.rerun()
    
    elif st.session_state.interview_phase == "completed":
        st.success("✅ Interview Completed")
        
        # Generate report manually
        risk_level, color = get_risk_level(st.session_state.risk_score)
        avg_attention = sum(st.session_state.attention_scores) / len(st.session_state.attention_scores) if st.session_state.attention_scores else 100
        avg_stress = sum(st.session_state.stress_scores) / len(st.session_state.stress_scores) if st.session_state.stress_scores else 0
        
        # Count violation types
        violation_counts = {}
        for v in st.session_state.violations_log:
            vtype = v['type']
            violation_counts[vtype] = violation_counts.get(vtype, 0) + 1
        
        report = {
            'report_metadata': {
                'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'candidate_name': st.session_state.candidate_name,
                'interview_id': st.session_state.interview_id,
                'start_time': st.session_state.start_time,
                'end_time': st.session_state.end_time
            },
            'integrity_score': {
                'cheating_risk_score': f"{st.session_state.risk_score:.1f}/100",
                'risk_level': risk_level,
                'risk_color': color,
                'verdict': get_status_message(st.session_state.risk_score, risk_level)
            },
            'attention_analysis': {
                'average_gaze_on_screen': f"{avg_attention:.1f}%",
                'off_screen_events': violation_counts.get('LOOKING_AWAY_REPEATED', 0),
                'attention_consistency': 'HIGH' if avg_attention > 80 else 'MEDIUM' if avg_attention > 60 else 'LOW'
            },
            'behavior_analysis': {
                'stress_level': f"{avg_stress:.1f}/100",
                'stress_category': 'HIGH' if avg_stress > 60 else 'MEDIUM' if avg_stress > 30 else 'LOW',
                'whispering_detected': violation_counts.get('WHISPERING', 0) > 0,
                'reading_pattern_detected': violation_counts.get('READING_PATTERN', 0) > 0
            },
            'anti_cheat_events': {
                'phone_detected': violation_counts.get('PHONE_DETECTED', 0) > 0,
                'multiple_people': violation_counts.get('MULTIPLE_FACES', 0) > 0,
                'suspicious_objects': violation_counts.get('SUSPICIOUS_OBJECT', 0),
                'no_face_events': violation_counts.get('NO_FACE', 0)
            },
            'violation_summary': {
                'total_violations': len(st.session_state.violations_log),
                'violation_breakdown': violation_counts,
                'detailed_violations': st.session_state.violations_log[-20:]
            }
        }
        
        # Save report
        os.makedirs('reports', exist_ok=True)
        report_file = f"reports/{st.session_state.interview_id}_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Display report
        st.header("📊 Interview Integrity Report")
        
        # Risk score
        risk_level = report['integrity_score']['risk_level']
        if risk_level == "CLEAN":
            st.markdown('<div class="status-clean">✅ CLEAN - No significant violations</div>', unsafe_allow_html=True)
        elif risk_level == "SUSPICIOUS":
            st.markdown('<div class="status-suspicious">⚠️ SUSPICIOUS - Review recommended</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-cheating">🚨 CHEATING - Multiple violations detected</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Risk Score", report['integrity_score']['cheating_risk_score'])
        with col2:
            st.metric("Total Violations", report['violation_summary']['total_violations'])
        with col3:
            st.metric("Attention Score", report['attention_analysis']['average_gaze_on_screen'])
        
        # Detailed sections

        
        with st.expander("👁️ Attention Analysis", expanded=True):
            st.json(report['attention_analysis'])
        
        with st.expander("🚨 Anti-Cheat Events", expanded=True):
            st.json(report['anti_cheat_events'])
        
        with st.expander("🎭 Behavior Analysis", expanded=True):
            st.json(report['behavior_analysis'])
        
        # Download report
        st.download_button(
            "📥 Download Full Report (JSON)",
            data=json.dumps(report, indent=2),
            file_name=f"{st.session_state.interview_id}_report.json",
            mime="application/json"
        )
        
        if st.button("🔄 Start New Interview"):
            # Reset everything
            st.session_state.clear()
            st.rerun()


if __name__ == "__main__":
    main()
