# Project Index

Quick navigation to all project files and documentation.

## 🚀 Getting Started

| File | Purpose | Start Here |
|------|---------|------------|
| [README.md](README.md) | Project overview and quick start | ⭐ START |
| [QUICKSTART.md](QUICKSTART.md) | 2-minute setup guide | ⭐ FAST |
| [install.sh](install.sh) | Automated installation | 🔧 RUN |
| [verify_installation.py](verify_installation.py) | Check setup | ✅ TEST |

## 📖 Documentation

| File | Content | Audience |
|------|---------|----------|
| [README.md](README.md) | Overview, features, quick start | Everyone |
| [QUICKSTART.md](QUICKSTART.md) | Fast setup and first run | New users |
| [USAGE.md](USAGE.md) | Detailed usage instructions | Users |
| [FEATURES.md](FEATURES.md) | Complete feature list | Users/Developers |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Code organization | Developers |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design and diagrams | Developers |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Completion status | Project managers |
| [INDEX.md](INDEX.md) | This file - navigation | Everyone |

## 💻 Application Files

### Main Applications
| File | Description | Usage |
|------|-------------|-------|
| [app.py](app.py) | Full PyQt5 GUI application | `python app.py` |
| [run_simple.py](run_simple.py) | OpenCV-only version | `python run_simple.py` |
| [test_components.py](test_components.py) | Component testing suite | `python test_components.py` |

### Core Modules (utils/)
| File | Purpose | Key Classes |
|------|---------|-------------|
| [face_tracker.py](utils/face_tracker.py) | Face detection + landmarks | `FaceTracker` |
| [gaze_estimator.py](utils/gaze_estimator.py) | Eye gaze estimation | `GazeEstimator` |
| [calibration.py](utils/calibration.py) | 9-point calibration | `GazeCalibration` |
| [object_detector.py](utils/object_detector.py) | YOLO detection | `ObjectDetector` |
| [id_tracker.py](utils/id_tracker.py) | Person tracking | `PersonTracker` |

### UI Components (ui/)
| File | Purpose | Key Classes |
|------|---------|-------------|
| [interface.py](ui/interface.py) | PyQt5 GUI | `MainWindow` |

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| [requirements.txt](requirements.txt) | Python dependencies |
| [.gitignore](.gitignore) | Git ignore rules |

## 📁 Directories

| Directory | Contents | Purpose |
|-----------|----------|---------|
| `models/` | Model files | dlib predictor, YOLO weights |
| `calibration/` | Calibration data | calibration.json |
| `captures/` | Saved images | Auto-captured detections |
| `utils/` | Core modules | Face, gaze, tracking logic |
| `ui/` | GUI components | PyQt5 interface |

## 📚 Documentation by Topic

### Installation & Setup
1. [README.md](README.md) - Installation section
2. [QUICKSTART.md](QUICKSTART.md) - Fast setup
3. [install.sh](install.sh) - Automated installer
4. [verify_installation.py](verify_installation.py) - Verification

### Usage & Features
1. [USAGE.md](USAGE.md) - Complete usage guide
2. [FEATURES.md](FEATURES.md) - Feature list
3. [QUICKSTART.md](QUICKSTART.md) - Quick reference

### Development & Architecture
1. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Code organization
2. [ARCHITECTURE.md](ARCHITECTURE.md) - System design
3. [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Status

### Troubleshooting
1. [README.md](README.md) - Troubleshooting section
2. [USAGE.md](USAGE.md) - Common issues
3. [QUICKSTART.md](QUICKSTART.md) - Quick fixes

## 🎯 Quick Access by Task

### I want to...

**Install the application**
→ Run `bash install.sh` or see [README.md](README.md)

**Run the application**
→ `python app.py` or see [QUICKSTART.md](QUICKSTART.md)

**Understand features**
→ Read [FEATURES.md](FEATURES.md)

**Learn how to use it**
→ Read [USAGE.md](USAGE.md)

**Understand the code**
→ Read [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

**See system design**
→ Read [ARCHITECTURE.md](ARCHITECTURE.md)

**Test components**
→ Run `python test_components.py`

**Verify installation**
→ Run `python verify_installation.py`

**Troubleshoot issues**
→ See [README.md](README.md) or [USAGE.md](USAGE.md)

**Customize parameters**
→ See [FEATURES.md](FEATURES.md) customization section

## 🔍 Find by Feature

### Face Tracking
- Code: [utils/face_tracker.py](utils/face_tracker.py)
- Docs: [FEATURES.md](FEATURES.md) - Section 1
- Usage: [USAGE.md](USAGE.md) - Face Tracking

### Eye Gaze Tracking
- Code: [utils/gaze_estimator.py](utils/gaze_estimator.py)
- Docs: [FEATURES.md](FEATURES.md) - Section 2
- Usage: [USAGE.md](USAGE.md) - Eye Gaze Tracking

### Calibration
- Code: [utils/calibration.py](utils/calibration.py)
- Docs: [FEATURES.md](FEATURES.md) - Section 4
- Usage: [USAGE.md](USAGE.md) - Calibration System

### Object Detection
- Code: [utils/object_detector.py](utils/object_detector.py)
- Docs: [FEATURES.md](FEATURES.md) - Section 5
- Usage: [USAGE.md](USAGE.md) - Object Detection

### Person Tracking
- Code: [utils/id_tracker.py](utils/id_tracker.py)
- Docs: [FEATURES.md](FEATURES.md) - Section 3
- Usage: [USAGE.md](USAGE.md) - Multiple People Detection

### User Interface
- Code: [ui/interface.py](ui/interface.py)
- Docs: [FEATURES.md](FEATURES.md) - Section 6
- Usage: [USAGE.md](USAGE.md) - UI Controls

## 📊 File Statistics

### Code Files
- Python modules: 11
- Total lines of code: ~940
- Documentation lines: ~1,300

### Documentation Files
- Markdown files: 8
- Total documentation: ~2,500 lines

### Configuration Files
- Setup scripts: 2
- Config files: 2

### Total Project Files: 20+

## 🎓 Learning Path

### Beginner
1. Read [README.md](README.md)
2. Follow [QUICKSTART.md](QUICKSTART.md)
3. Run `python app.py`
4. Read [USAGE.md](USAGE.md)

### Intermediate
1. Read [FEATURES.md](FEATURES.md)
2. Run `python test_components.py`
3. Explore [utils/](utils/) modules
4. Customize parameters

### Advanced
1. Read [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
2. Read [ARCHITECTURE.md](ARCHITECTURE.md)
3. Study individual modules
4. Extend functionality

## 🔗 External Resources

### Models
- dlib predictor: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
- YOLOv8n: Auto-downloads from Ultralytics

### Libraries
- OpenCV: https://opencv.org/
- dlib: http://dlib.net/
- YOLO: https://github.com/ultralytics/ultralytics
- PyQt5: https://www.riverbankcomputing.com/software/pyqt/

## 📞 Support

### Documentation
- Quick help: [QUICKSTART.md](QUICKSTART.md)
- Detailed help: [USAGE.md](USAGE.md)
- Technical details: [ARCHITECTURE.md](ARCHITECTURE.md)

### Testing
- Verify setup: `python verify_installation.py`
- Test components: `python test_components.py`
- Simple demo: `python run_simple.py`

## ✅ Checklist

### Before First Run
- [ ] Read [README.md](README.md)
- [ ] Run `bash install.sh`
- [ ] Run `python verify_installation.py`
- [ ] Check camera permissions

### First Run
- [ ] Run `python app.py`
- [ ] Complete calibration
- [ ] Test with face tracking
- [ ] Enable object detection
- [ ] Check captures folder

### Development
- [ ] Read [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- [ ] Read [ARCHITECTURE.md](ARCHITECTURE.md)
- [ ] Run component tests
- [ ] Explore code modules

## 🎉 Quick Commands

```bash
# Install
bash install.sh

# Verify
python verify_installation.py

# Run GUI
python app.py

# Run simple
python run_simple.py

# Test
python test_components.py
```

---

**Navigation Tip**: Use Ctrl+F (Cmd+F on Mac) to search this index for specific topics.

**Last Updated**: December 1, 2025
**Project Status**: ✅ Complete
**Version**: 1.0
