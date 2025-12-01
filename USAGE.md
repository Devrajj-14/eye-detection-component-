# Usage Guide

## Quick Start

1. Install dependencies:
```bash
bash install.sh
# or manually:
pip install -r requirements.txt
```

2. Download the facial landmark model:
```bash
cd models
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
```

3. Run the application:
```bash
python app.py
```

## Features Overview

### Face Tracking
- Detects all faces in the camera view
- Assigns unique IDs to each person
- Tracks people across frames using centroid tracking
- Displays 68 facial landmarks per face
- Shows head pose orientation (pitch, yaw, roll)

### Eye Gaze Tracking
- Estimates gaze direction for each person
- Displays gaze vector as an arrow
- Classifies gaze into:
  - looking_center
  - looking_left
  - looking_right
  - looking_up
  - looking_down

### Calibration System
1. Click "Start Calibration" button
2. A red dot will appear on screen
3. Look directly at the dot (keep head still)
4. The dot will move to 9 different positions
5. Each position is sampled for 1 second
6. After all 9 points, calibration is complete
7. Calibration data saved to `calibration/calibration.json`

### Object Detection
1. Click "Start Detection" to enable
2. YOLO detects objects in real-time
3. Objects with confidence > 0.55 are highlighted
4. Frames with detected objects are auto-saved to `captures/`
5. Detection log saved to `captures/log.json`

### UI Controls
- **Start Calibration**: Begin 9-point calibration routine
- **Start Detection**: Enable/disable object detection
- **Open Captures Folder**: View saved images

## Output Data Structure

### Person Data (per frame)
```json
{
  "id": 1,
  "face_box": [x, y, w, h],
  "gaze_direction": "looking_center",
  "landmarks": [[x1, y1], [x2, y2], ...],
  "head_pose": [pitch, yaw, roll]
}
```

### Detection Log
```json
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
```

## Performance Tips

- Runs on CPU (no GPU required)
- Target: >15 FPS on modern laptops
- Reduce camera resolution if FPS drops
- Close other applications for better performance
- Good lighting improves face detection accuracy

## Troubleshooting

### "Could not load shape_predictor_68_face_landmarks.dat"
Download the model file:
```bash
cd models
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
```

### Low FPS
- Reduce camera resolution in `app.py`
- Disable object detection when not needed
- Ensure good lighting for faster face detection

### Camera not found
- Check camera permissions
- Try different camera index: `cv2.VideoCapture(1)` instead of `0`

### YOLO model download fails
- Check internet connection
- Model auto-downloads on first run
- Manually download from: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
