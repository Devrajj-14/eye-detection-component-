"""
Test sensitivity improvements
"""
import cv2
import time
from utils.face_tracker import FaceTracker
from utils.gaze_estimator import GazeEstimator
from utils.object_detector import ObjectDetector


def test_sensitivity():
    print("🎯 Testing Sensitivity Improvements")
    print("=" * 60)
    
    # Initialize
    face_tracker = FaceTracker()
    gaze_estimator = GazeEstimator()
    object_detector = ObjectDetector()
    
    print("✅ Components initialized")
    print(f"📊 Gaze threshold: 1.5px (ULTRA SENSITIVE)")
    print(f"📊 Object confidence: {object_detector.confidence_threshold} (ULTRA LOW)")
    print("=" * 60)
    
    print("\n🧪 TEST SCENARIOS:")
    print("1. Look slightly off screen → Should detect in 0.33s")
    print("2. Show half phone → Should detect immediately")
    print("3. Show edge of phone → Should detect within 1s")
    print("4. Move head while eyes on screen → Should NOT alert")
    print("=" * 60)
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    looking_away_frames = 0
    frame_count = 0
    start_time = time.time()
    
    print("\n▶️ Starting test... Press 'q' to quit\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Detect face
        face_boxes = face_tracker.detect_faces(frame)
        
        # Detect objects
        detections = object_detector.detect(frame)
        
        if len(detections) > 0:
            print(f"\n🔍 Frame {frame_count}: {len(detections)} object(s) detected")
            for det in detections:
                print(f"   - {det['class_name']}: {det['confidence']:.3f}")
        
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
                
                # Check if looking away
                if gaze_direction in ["looking_left", "looking_right", "looking_down", "looking_up"]:
                    looking_away_frames += 1
                    
                    if looking_away_frames == 10:  # 0.33 seconds at 30fps
                        elapsed = time.time() - start_time
                        print(f"\n🚨 ALERT: Eyes off screen detected!")
                        print(f"   Direction: {gaze_direction}")
                        print(f"   Detection time: {elapsed:.2f}s")
                        print(f"   Frames: {looking_away_frames}")
                        start_time = time.time()
                else:
                    if looking_away_frames > 0:
                        looking_away_frames = 0
                        start_time = time.time()
                
                # Draw face tracking
                x, y, w, h = box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Draw gaze
                gaze_estimator.draw_gaze(frame, landmarks, gaze_vector, gaze_direction)
                
                # Draw status
                if gaze_direction == "looking_center":
                    status = "ON SCREEN ✅"
                    color = (0, 255, 0)
                else:
                    status = f"OFF SCREEN 🚨 ({gaze_direction})"
                    color = (0, 0, 255)
                
                cv2.putText(frame, status, (10, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                
                cv2.putText(frame, f"Looking away frames: {looking_away_frames}/10", (10, 80),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw detections
        if len(detections) > 0:
            object_detector.draw_detections(frame, detections)
        
        cv2.imshow('Sensitivity Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_sensitivity()
