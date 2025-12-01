# Quick Start Guide

## Installation (2 minutes)

```bash
# Clone or download the project
cd openface_interviewer

# Run installer
bash install.sh

# Verify
python verify_installation.py
```

## Run Application (1 command)

```bash
# Full GUI version
python app.py

# OR simple OpenCV version
python run_simple.py
```

## First Time Setup

### Step 1: Calibration (30 seconds)
1. Click "Start Calibration"
2. Look at 9 red dots (1 sec each)
3. Done! Calibration saved automatically

### Step 2: Enable Detection (optional)
1. Click "Start Detection"
2. Objects detected and saved automatically

## Keyboard Shortcuts (Simple Mode)

| Key | Action |
|-----|--------|
| `c` | Start/Stop Calibration |
| `d` | Toggle Object Detection |
| `q` | Quit |

## What You'll See

### On Screen
- Green boxes around faces
- Person ID labels
- 68 facial landmarks (dots)
- Head pose axes (RGB lines)
- Gaze direction arrows (magenta)
- FPS counter
- People count

### During Calibration
- Red calibration dots
- Progress counter (1/9, 2/9, etc.)
- Instructions overlay

### With Detection Enabled
- Yellow boxes around objects
- Class labels + confidence
- Auto-saved to `captures/`

## Output Files

```
captures/
├── object_20241201_143022.jpg    # Auto-saved images
└── log.json                       # Detection log

calibration/
└── calibration.json               # Calibration data
```

## Common Issues

### "Camera not found"
```bash
# Check camera permissions
# Try different camera:
# Edit app.py line: cv2.VideoCapture(1)  # instead of 0
```

### "Model not found"
```bash
cd models
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
```

### "Low FPS"
- Reduce camera resolution in app.py
- Disable object detection
- Improve lighting

## Testing Individual Components

```bash
python test_components.py

# Then select:
# 1 - Face Detection
# 2 - Gaze Estimation
# 3 - Object Detection
# 4 - Person Tracking
```

## Performance Expectations

| Metric | Value |
|--------|-------|
| FPS | 15-30 |
| Latency | <100ms |
| Max People | 5+ |
| CPU Usage | 40-60% |

## Next Steps

1. ✅ Run `python app.py`
2. ✅ Complete calibration
3. ✅ Test with multiple people
4. ✅ Enable object detection
5. ✅ Check `captures/` folder
6. 📖 Read [USAGE.md](USAGE.md) for details
7. 🔧 Customize parameters
8. 🚀 Build your application!

## Support

- Check [USAGE.md](USAGE.md) for detailed instructions
- See [FEATURES.md](FEATURES.md) for complete feature list
- Review [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture

## One-Line Install & Run

```bash
bash install.sh && python verify_installation.py && python app.py
```

That's it! 🎉
