"""
Simple OpenCV-only version (no PyQt5 GUI)
For testing without GUI dependencies
"""
import cv2
import time
from utils.face_tracker import FaceTracker
from utils.gaze_estimator import GazeEstimator
from utils.calibration import GazeCalibration
from utils.object_detector import ObjectDetector
from utils.id_tracker import PersonTracker


def main():
    # Initialize components
    face_tracker = FaceTracker()
    gaze_estimator = GazeEstimator()
    calibration = GazeCalibration()
    object_detector = ObjectDetector()
    person_tracker = PersonTracker()
    
    # Camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # State
    detection_enabled = False
    fps = 0
    frame_count = 0
    start_time = time.time()
    calibration_start_time = None
    calibration_sample_duration = 1.0
    
    print("Controls:")
    print("  'c' - Start/Stop Calibration")
    print("  'd' - Toggle Object Detection")
    print("  'q' - Quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Calculate FPS
        elapsed = time.time() - start_time
        if elapsed > 1.0:
            fps = frame_count / elapsed
            frame_count = 0
            start_time = time.time()
        
        # Detect faces
        face_boxes = face_tracker.detect_faces(frame)
        tracked_objects = person_tracker.update(face_boxes)
        
        # Process each face
        for box in face_boxes:
            person_id = person_tracker.get_id_for_box(box)
            landmarks = face_tracker.get_landmarks(frame, box)
            head_pose = face_tracker.get_head_pose(landmarks, frame.shape)
            gaze_vector, gaze_direction = gaze_estimator.estimate_gaze(
                frame, landmarks, head_pose
            )
            
            # Draw
            x, y, w, h = box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            if person_id is not None:
                cv2.putText(frame, f"ID: {person_id}", (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            face_tracker.draw_landmarks(frame, landmarks)
            face_tracker.draw_head_pose(frame, landmarks, head_pose)
            gaze_estimator.draw_gaze(frame, landmarks, gaze_vector, gaze_direction)
            
            # Calibration sampling
            if calibration.is_calibrating and landmarks is not None:
                if calibration_start_time is None:
                    calibration_start_time = time.time()
                
                if time.time() - calibration_start_time >= calibration_sample_duration:
                    left_eye_region, left_box = gaze_estimator.get_eye_region(
                        frame, landmarks, gaze_estimator.LEFT_EYE
                    )
                    right_eye_region, right_box = gaze_estimator.get_eye_region(
                        frame, landmarks, gaze_estimator.RIGHT_EYE
                    )
                    
                    left_iris = gaze_estimator.get_iris_center(left_eye_region)
                    right_iris = gaze_estimator.get_iris_center(right_eye_region)
                    
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
                    
                    calibration.add_calibration_sample(eye_features)
                    calibration_start_time = None
        
        # Calibration UI
        if calibration.is_calibrating:
            calibration.draw_calibration_point(frame)
        
        # Object detection
        if detection_enabled:
            detections = object_detector.detect(frame)
            if len(detections) > 0:
                object_detector.draw_detections(frame, detections)
                object_detector.save_detection(frame, detections)
        
        # Draw info
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"People: {len(face_boxes)}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if calibration.is_calibrating:
            cv2.putText(frame, "CALIBRATING", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif calibration.model_x is not None:
            cv2.putText(frame, "Calibrated", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if detection_enabled:
            cv2.putText(frame, "Detection: ON", (10, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        cv2.imshow("OpenFace Multi-Person Tracker", frame)
        
        # Handle keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            if calibration.is_calibrating:
                calibration.is_calibrating = False
                print("Calibration stopped")
            else:
                calibration.start_calibration()
                calibration_start_time = None
                print("Calibration started")
        elif key == ord('d'):
            detection_enabled = not detection_enabled
            print(f"Detection: {'ON' if detection_enabled else 'OFF'}")
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
