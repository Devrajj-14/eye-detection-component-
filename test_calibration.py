"""
Quick test to verify calibration is working
"""
import cv2
from utils.face_tracker import FaceTracker
from utils.gaze_estimator import GazeEstimator


def test_calibration():
    print("🎯 Testing Calibration System")
    print("=" * 50)
    
    # Initialize
    face_tracker = FaceTracker()
    gaze_estimator = GazeEstimator()
    
    # Check calibration status
    if gaze_estimator.is_calibrated:
        print("✅ Calibration loaded successfully!")
        print(f"📊 Screen bounds: {gaze_estimator.screen_bounds}")
    else:
        print("⚠️ No calibration found")
        print("💡 Run: python calibrate_screen.py")
        print()
        print("Continuing with uncalibrated mode...")
    
    print("=" * 50)
    print("Instructions:")
    print("- Look around the screen")
    print("- System will show if gaze is ON or OFF screen")
    print("- Press 'q' to quit")
    print("=" * 50)
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect face
        face_boxes = face_tracker.detect_faces(frame)
        
        if len(face_boxes) > 0:
            box = face_boxes[0]
            landmarks = face_tracker.get_landmarks(frame, box)
            
            if landmarks is not None:
                # Get head pose
                head_pose = face_tracker.get_head_pose(landmarks, frame.shape)
                
                # Get gaze
                gaze_vector, gaze_direction = gaze_estimator.estimate_gaze(
                    frame, landmarks, head_pose
                )
                
                # Draw face tracking
                x, y, w, h = box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Draw gaze
                gaze_estimator.draw_gaze(frame, landmarks, gaze_vector, gaze_direction)
                
                # Check if on screen (if calibrated)
                if gaze_estimator.is_calibrated:
                    # Extract gaze values from estimate_gaze
                    # For now, use direction as proxy
                    if gaze_direction == "looking_center":
                        status = "ON SCREEN ✅"
                        color = (0, 255, 0)
                    else:
                        status = "OFF SCREEN 🚨"
                        color = (0, 0, 255)
                    
                    cv2.putText(frame, status, (10, 40),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
                else:
                    cv2.putText(frame, "UNCALIBRATED MODE", (10, 40),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
                
                cv2.putText(frame, f"Gaze: {gaze_direction}", (10, 80),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.imshow('Calibration Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    test_calibration()
