# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     OpenFace 3.0 System                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Camera Input (CV2)                      │
│                    1280x720 @ 30 FPS                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Face Detection (dlib)                     │
│              Detect all faces in frame                       │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│   Landmark Extraction     │   │   Person ID Tracking      │
│   68 points per face      │   │   Centroid-based          │
└───────────────────────────┘   └───────────────────────────┘
                │                           │
                ▼                           │
┌───────────────────────────┐               │
│   Head Pose Estimation    │               │
│   Pitch, Yaw, Roll        │               │
└───────────────────────────┘               │
                │                           │
                ▼                           │
┌───────────────────────────┐               │
│   Eye Region Extraction   │               │
│   Left & Right eyes       │               │
└───────────────────────────┘               │
                │                           │
                ▼                           │
┌───────────────────────────┐               │
│   Iris Detection          │               │
│   Pupil center tracking   │               │
└───────────────────────────┘               │
                │                           │
                ▼                           │
┌───────────────────────────┐               │
│   Gaze Estimation         │               │
│   Direction + Vector      │               │
└───────────────────────────┘               │
                │                           │
                └───────────┬───────────────┘
                            ▼
            ┌───────────────────────────┐
            │   Calibration (Optional)  │
            │   9-point mapping         │
            └───────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Object Detection (YOLO)                     │
│              Parallel processing pipeline                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Visualization Layer                       │
│   • Face boxes          • Gaze arrows                        │
│   • Landmarks           • Person IDs                         │
│   • Head pose axes      • Object boxes                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Output Layer                            │
│   • GUI Display         • Auto-capture                       │
│   • FPS Counter         • JSON Logging                       │
└─────────────────────────────────────────────────────────────┘
```

## Component Interaction

```
┌──────────────┐
│   app.py     │  Main Controller
└──────┬───────┘
       │
       ├─────────────┐
       │             │
       ▼             ▼
┌─────────────┐  ┌─────────────┐
│ FaceTracker │  │ GazeEstim.  │
└──────┬──────┘  └──────┬──────┘
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│ PersonTrack │  │ Calibration │
└─────────────┘  └─────────────┘
       │                │
       └────────┬───────┘
                ▼
         ┌─────────────┐
         │ ObjectDetect│
         └──────┬──────┘
                │
                ▼
         ┌─────────────┐
         │  Interface  │
         └─────────────┘
```

## Data Flow Pipeline

### Frame Processing (per frame)

```
1. Capture Frame
   └─> 1280x720 BGR image

2. Face Detection
   └─> List of bounding boxes [(x,y,w,h), ...]

3. For Each Face:
   ├─> Extract 68 landmarks
   ├─> Calculate head pose (pitch, yaw, roll)
   ├─> Extract eye regions
   ├─> Detect iris centers
   ├─> Estimate gaze vector
   └─> Classify gaze direction

4. Person Tracking
   └─> Assign/update person IDs

5. Calibration (if active)
   └─> Collect eye features at calibration points

6. Object Detection (if enabled)
   └─> YOLO inference → detections

7. Visualization
   ├─> Draw face boxes
   ├─> Draw landmarks
   ├─> Draw head pose axes
   ├─> Draw gaze arrows
   ├─> Draw person IDs
   └─> Draw object boxes

8. Output
   ├─> Display frame
   ├─> Save detections (if any)
   └─> Update UI status
```

## Module Dependencies

```
app.py
├── utils/face_tracker.py
│   └── dlib
│       └── opencv
├── utils/gaze_estimator.py
│   └── opencv
│       └── numpy
├── utils/calibration.py
│   └── sklearn
│       └── numpy
├── utils/object_detector.py
│   └── ultralytics
│       └── opencv
├── utils/id_tracker.py
│   └── scipy
│       └── numpy
└── ui/interface.py
    └── PyQt5
        └── opencv
```

## Threading Model

```
┌─────────────────────────────────────┐
│         Main Thread (GUI)           │
│  • PyQt5 event loop                 │
│  • UI updates                       │
│  • Button handlers                  │
└─────────────────┬───────────────────┘
                  │
                  │ QTimer (30ms)
                  │
                  ▼
┌─────────────────────────────────────┐
│      Processing Thread              │
│  • Frame capture                    │
│  • Face detection                   │
│  • Gaze estimation                  │
│  • Object detection                 │
│  • Visualization                    │
└─────────────────────────────────────┘
```

## State Management

```
OpenFaceApp State:
├── current_frame: np.ndarray
├── is_running: bool
├── detection_enabled: bool
├── fps: float
├── frame_count: int
└── calibration_start_time: float

Calibration State:
├── is_calibrating: bool
├── current_point_idx: int
├── calibration_data: list
├── model_x: Ridge
└── model_y: Ridge

PersonTracker State:
├── next_id: int
├── objects: dict {id: centroid}
└── disappeared: dict {id: count}
```

## File I/O Operations

```
Read Operations:
├── Camera: cv2.VideoCapture(0)
├── Models: dlib.shape_predictor(path)
├── Calibration: json.load(calibration.json)
└── Config: (hardcoded parameters)

Write Operations:
├── Captures: cv2.imwrite(captures/*.jpg)
├── Logs: json.dump(log.json)
└── Calibration: json.dump(calibration.json)
```

## Performance Optimization Strategies

### 1. Model Selection
- **dlib**: Lightweight face detector
- **YOLOv8n**: Smallest YOLO variant (6MB)
- **CPU-optimized**: No GPU dependencies

### 2. Processing Pipeline
- **Parallel detection**: Face and object detection can run independently
- **Conditional processing**: Object detection only when enabled
- **Frame skipping**: Optional for lower-end hardware

### 3. Memory Management
- **In-place operations**: Minimize array copies
- **Efficient data structures**: NumPy arrays
- **Garbage collection**: Proper cleanup on exit

### 4. Algorithmic Efficiency
- **Centroid tracking**: O(n²) but fast for small n
- **Landmark caching**: Reuse when possible
- **Vectorized operations**: NumPy for speed

## Scalability Considerations

### Current Limits
- **People**: 5-10 simultaneous (CPU dependent)
- **FPS**: 15-30 on modern CPU
- **Resolution**: 1280x720 optimal

### Scaling Options
1. **GPU Acceleration**: Add CUDA support for YOLO
2. **Multi-threading**: Separate threads per person
3. **Frame skipping**: Process every Nth frame
4. **Resolution reduction**: Lower camera resolution
5. **Model optimization**: ONNX/TensorRT conversion

## Error Handling

```
Try-Catch Hierarchy:
├── Camera access
│   └─> Fallback to test image
├── Model loading
│   └─> Error message + exit
├── Face detection
│   └─> Continue with empty list
├── Landmark extraction
│   └─> Skip gaze estimation
└── File I/O
    └─> Create directories if missing
```

## Configuration Points

### Runtime Configuration
- Camera index: `cv2.VideoCapture(0)`
- Resolution: `cap.set(CAP_PROP_WIDTH, 1280)`
- FPS target: `timer.start(30)`

### Model Configuration
- Face detector: dlib frontal face detector
- Landmark model: 68-point predictor
- Object detector: YOLOv8n

### Algorithm Configuration
- Detection confidence: 0.55
- Tracking persistence: 30 frames
- Calibration points: 9 (3x3 grid)
- Sample duration: 1.0 seconds

## Extension Points

### Adding New Features
1. **New detector**: Implement in `utils/`
2. **New visualization**: Add to visualization layer
3. **New output format**: Extend output layer
4. **New UI element**: Modify `ui/interface.py`

### Integration Points
- **Database**: Add logging to database
- **Network**: Stream over network
- **Analytics**: Add real-time analytics
- **Export**: Add data export formats

## Security Considerations

### Privacy
- Local processing only (no cloud)
- No data transmission
- User controls capture

### Data Storage
- Images saved locally
- JSON logs unencrypted
- Calibration data personal

### Recommendations
- Encrypt sensitive data
- Add user consent flows
- Implement data retention policies
- Add access controls for production
