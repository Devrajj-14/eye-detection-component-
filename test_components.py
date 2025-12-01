"""
Test individual components without GUI
"""
import cv2
import time
from utils.face_tracker import FaceTracker
from utils.gaze_estimator import GazeEstimator
from utils.object_detector import ObjectDetector
from utils.id_tracker import PersonTracker


def test_face_detection():
    """Test face detection and landmark extraction"""
    print("Testing face detection...")
    
    face_tracker = FaceTracker()
    cap = cv2.VideoCapture(0)
    
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect faces
        faces = face_tracker.detect_faces(frame)
        print(f"Detected {len(faces)} faces")
        
        # Draw boxes
        for box in faces:
            x, y, w, h = box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Get landmarks
            landmarks = face_tracker.get_landmarks(frame, box)
            if landmarks is not None:
                face_tracker.draw_landmarks(frame, landmarks)
                
                # Get head pose
                head_pose = face_tracker.get_head_pose(landmarks, frame.shape)
                face_tracker.draw_head_pose(frame, landmarks, head_pose)
        
        cv2.imshow("Face Detection Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


def test_gaze_estimation():
    """Test gaze estimation"""
    print("Testing gaze estimation...")
    
    face_tracker = FaceTracker()
    gaze_estimator = GazeEstimator()
    cap = cv2.VideoCapture(0)
    
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        faces = face_tracker.detect_faces(frame)
        
        for box in faces:
            x, y, w, h = box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            landmarks = face_tracker.get_landmarks(frame, box)
            if landmarks is not None:
                head_pose = face_tracker.get_head_pose(landmarks, frame.shape)
                gaze_vector, direction = gaze_estimator.estimate_gaze(
                    frame, landmarks, head_pose
                )
                
                gaze_estimator.draw_gaze(frame, landmarks, gaze_vector, direction)
                print(f"Gaze direction: {direction}")
        
        cv2.imshow("Gaze Estimation Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


def test_object_detection():
    """Test YOLO object detection"""
    print("Testing object detection...")
    
    detector = ObjectDetector()
    cap = cv2.VideoCapture(0)
    
    print("Press 'q' to quit, 's' to save detection")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        detections = detector.detect(frame)
        detector.draw_detections(frame, detections)
        
        if len(detections) > 0:
            print(f"Detected {len(detections)} objects:")
            for det in detections:
                print(f"  - {det['class_name']}: {det['confidence']:.2f}")
        
        cv2.imshow("Object Detection Test", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s') and len(detections) > 0:
            filepath = detector.save_detection(frame, detections)
            print(f"Saved to: {filepath}")
    
    cap.release()
    cv2.destroyAllWindows()


def test_person_tracking():
    """Test multi-person ID tracking"""
    print("Testing person tracking...")
    
    face_tracker = FaceTracker()
    person_tracker = PersonTracker()
    cap = cv2.VideoCapture(0)
    
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        faces = face_tracker.detect_faces(frame)
        tracked = person_tracker.update(faces)
        
        for box in faces:
            person_id = person_tracker.get_id_for_box(box)
            x, y, w, h = box
            
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"ID: {person_id}", (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.putText(frame, f"Tracked: {len(tracked)}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow("Person Tracking Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print("Component Tests")
    print("1. Face Detection")
    print("2. Gaze Estimation")
    print("3. Object Detection")
    print("4. Person Tracking")
    
    choice = input("Select test (1-4): ")
    
    if choice == "1":
        test_face_detection()
    elif choice == "2":
        test_gaze_estimation()
    elif choice == "3":
        test_object_detection()
    elif choice == "4":
        test_person_tracking()
    else:
        print("Invalid choice")
