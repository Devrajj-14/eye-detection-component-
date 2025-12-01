# OpenFace 3.0 Multi-Person Tracker - Project Structure

## Overview
Complete computer vision application for multi-person face tracking, eye gaze estimation, calibration, and object detection.

## Directory Structure

```
openface_interviewer/
│
├── app.py                      # Main application with PyQt5 GUI
├── run_simple.py               # OpenCV-only version (no GUI)
├── test_components.py          # Individual component tests
├── requirements.txt            # Python dependencies
├── install.sh                  # Installation script
├── README.md                   # Quick start guide
├── USAGE.md                    # Detailed usage instructions
├── PROJECT_STRUCTURE.md        # This file
│
├── utils/                      # Core functionality modules
│   ├── __init__.py
│   ├── face_tracker.py         # Face detection + landmarks (OpenFace 3.0)
│   ├── gaze_estimator.py       # Eye gaze direction estimation
│   ├── calibration.py          # 9-point calibration system
│   ├── object_detector.py      # YOLO object detection
│   └── id_tracker.py           # Centroid-based person tracking
│
├── ui/                         # GUI components
│   ├── __init__.py
│   └── interface.py            # PyQt5 main window
│
├── models/                     # Model files (not in git)
│   ├── .gitkeep
│   ├── shape_predictor_68_face_landmarks.dat  # dlib model
│   └── yolov8n.pt              # YOLO model (auto-downloads)
│
├── calibration/                # Calibration data
│   ├── .gitkeep
│   └── calibration.json        # Saved calibration matrix
│
└── captures/                   # Auto-saved images
    ├── .gitkeep
    ├── log.json                # Detection log
    └── object_*.jpg            # Captured images
```

## Component Details

### 1. face_tracker.py
**Purpose**: Face detection and landmark extraction

**Key Classes**:
- `FaceTracker`: Main face tracking class

**Methods**:
- `detect_faces(frame)`: Detect all faces, returns bounding boxes
- `get_landmarks(frame, box)`: Extract 68 facial landmarks
- `get_head_pose(landmarks, frame_shape)`: Calculate pitch/yaw/roll
- `draw_landmarks(frame, landmarks)`: Visualize landmarks
- `draw_head_pose(frame, landmarks, pose)`: Draw pose axes

**Dependencies**: dlib, OpenCV

### 2. gaze_estimator.py
**Purpose**: Eye gaze direction estimation

**Key Classes**:
- `GazeEstimator`: Gaze estimation engine

**Methods**:
- `get_eye_region(frame, landmarks, eye_points)`: Extract eye ROI
- `get_iris_center(eye_region)`: Detect iris position
- `estimate_gaze(frame, landmarks, head_pose)`: Calculate gaze vector
- `draw_gaze(frame, landmarks, gaze_vector, direction)`: Visualize gaze

**Output Directions**:
- looking_center
- looking_left
- looking_right
- looking_up
- looking_down

### 3. calibration.py
**Purpose**: 9-point calibration for accurate gaze mapping

**Key Classes**:
- `GazeCalibration`: Calibration system

**Methods**:
- `start_calibration()`: Begin calibration routine
- `add_calibration_sample(eye_features)`: Record calibration point
- `finish_calibration()`: Build regression model
- `predict_gaze_point(eye_features)`: Map gaze to screen coordinates
- `save_calibration()` / `load_calibration()`: Persist calibration

**Calibration Process**:
1. Display 9 points in 3x3 grid
2. User looks at each point for 1 second
3. Record eye features + screen coordinates
4. Train Ridge regression model
5. Save to calibration.json

### 4. object_detector.py
**Purpose**: Real-time object detection with auto-capture

**Key Classes**:
- `ObjectDetector`: YOLO-based detector

**Methods**:
- `detect(frame)`: Run YOLO inference
- `save_detection(frame, detections)`: Auto-save detected objects
- `draw_detections(frame, detections)`: Visualize bounding boxes

**Features**:
- Confidence threshold: 0.55
- Auto-saves frames with detections
- Logs to captures/log.json

### 5. id_tracker.py
**Purpose**: Track multiple people across frames

**Key Classes**:
- `PersonTracker`: Centroid-based tracker

**Methods**:
- `register(centroid)`: Add new person
- `update(face_boxes)`: Update tracking with new detections
- `get_id_for_box(box)`: Get person ID for face box

**Algorithm**:
- Centroid tracking with Hungarian matching
- Handles occlusions and re-appearances
- Max disappeared frames: 30

### 6. interface.py
**Purpose**: PyQt5 GUI

**Key Classes**:
- `MainWindow`: Main application window

**UI Elements**:
- Video display (1280x720)
- Status bar
- Buttons: Start Calibration, Start Detection, Open Captures Folder

**Features**:
- Real-time video rendering
- Button event handlers
- Status updates

### 7. app.py
**Purpose**: Main application controller

**Key Classes**:
- `OpenFaceApp`: Application orchestrator

**Main Loop**:
```python
while True:
    read camera
    detect faces
    track people
    estimate gaze
    run calibration if needed
    detect objects
    save images if objects found
    render UI output
```

## Data Flow

```
Camera Frame
    ↓
Face Detection (dlib)
    ↓
Landmark Extraction (68 points)
    ↓
    ├─→ Head Pose Estimation
    ├─→ Eye Region Extraction
    │       ↓
    │   Iris Detection
    │       ↓
    │   Gaze Estimation
    │       ↓
    │   Calibration (optional)
    │
    └─→ Person ID Tracking
            ↓
        Visualization
            ↓
        Display + Save
```

## Performance Targets

- **FPS**: >15 on CPU
- **Latency**: <100ms per frame
- **Accuracy**: 
  - Face detection: >95%
  - Gaze direction: ~80%
  - Object detection: >70%

## Model Requirements

### dlib Face Predictor
- File: `shape_predictor_68_face_landmarks.dat`
- Size: ~99MB
- Download: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2

### YOLOv8n
- File: `yolov8n.pt`
- Size: ~6MB
- Auto-downloads on first run

## Configuration

### Camera Settings (app.py)
```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
```

### Detection Threshold (object_detector.py)
```python
confidence_threshold = 0.55
```

### Calibration Grid (calibration.py)
```python
# 9 points at (0.2, 0.5, 0.8) x (0.2, 0.5, 0.8)
```

### Tracking Parameters (id_tracker.py)
```python
max_disappeared = 30  # frames
```

## Running the Application

### Full GUI Version
```bash
python app.py
```

### Simple OpenCV Version
```bash
python run_simple.py
```

### Component Tests
```bash
python test_components.py
```

## Output Files

### Calibration Data
```json
{
  "screen_width": 1920,
  "screen_height": 1080,
  "calibration_data": [...],
  "model_x_coef": [...],
  "model_y_coef": [...]
}
```

### Detection Log
```json
[
  {
    "timestamp": "20241201_143022_123456",
    "filename": "object_20241201_143022_123456.jpg",
    "detections": [
      {
        "class": "person",
        "confidence": 0.87
      }
    ]
  }
]
```

## Dependencies

- opencv-python: Camera + image processing
- numpy: Numerical operations
- scipy: Distance calculations
- PyQt5: GUI framework
- ultralytics: YOLO models
- dlib: Face detection + landmarks
- scikit-learn: Calibration regression

## CPU Optimization

- Uses lightweight models (YOLOv8n)
- Efficient landmark detection (dlib)
- Minimal preprocessing
- Frame skipping for object detection (optional)
- No GPU required

## Future Enhancements

- [ ] Multi-camera support
- [ ] 3D gaze estimation
- [ ] Attention heatmaps
- [ ] Emotion recognition
- [ ] Export to CSV/JSON
- [ ] Real-time analytics dashboard
