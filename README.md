# 👁️ Eye Detection Interview AI

AI-powered interview integrity system with real-time eye tracking, gaze detection, and cheating prevention.

## 🎯 Features

### Core Detection
- **👁️ Eye Gaze Tracking** - Iris-based gaze estimation
- **📱 Phone Detection** - YOLO-based object detection
- **👥 Multiple People Detection** - Face counting and tracking
- **🎭 Behavior Analysis** - Stress, whispering, reading patterns
- **⚠️ Looking Away Detection** - Triggers alert after 0.8 seconds

### Monitoring
- **Real-time Risk Scoring** - 0-100 scale with decay
- **Violation Logging** - Timestamped with screenshots
- **Attention Tracking** - Continuous attention score
- **FPS Monitoring** - Performance tracking

### Interview Management
- **Candidate Tracking** - Name and ID management
- **Session Recording** - Start/end timestamps
- **Evidence Collection** - Screenshot capture
- **Integrity Reports** - JSON export with full details

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Webcam
- macOS/Linux/Windows

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/eyedetection-interviewAI.git
cd eyedetection-interviewAI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download models
python download_models.py
```

### Run Interview System

```bash
streamlit run pro_interview_system.py
```

Open browser to: http://localhost:8501

## 📋 Usage

### 1. Setup Interview
- Enter candidate name
- Enter interview ID
- Click "Start Interview"

### 2. During Interview
- System monitors in real-time
- Violations logged automatically
- Risk score updates continuously

### 3. End Interview
- Click "End Interview"
- View integrity report
- Download JSON report

## 🎯 Detection Thresholds

| Detection | Threshold | Time |
|-----------|-----------|------|
| Looking Away | 25 frames | ~0.8s |
| Phone Detection | 25% confidence | Instant |
| Multiple People | 2+ faces | 5 frames |
| No Face | 90 frames | 3s |

## 📊 System Architecture

```
┌─────────────────────────────────────────┐
│         Streamlit Web Interface         │
├─────────────────────────────────────────┤
│  Face Tracking  │  Gaze Estimation      │
│  Object Detection │ Behavior Analysis   │
│  Risk Scoring   │  Violation Logging    │
└─────────────────────────────────────────┘
         │                    │
    ┌────▼────┐         ┌────▼────┐
    │ OpenCV  │         │  YOLO   │
    │ dlib    │         │ v8      │
    └─────────┘         └─────────┘
```

## 🔧 Configuration

### Sensitivity Settings

**Gaze Detection:**
```python
# In utils/gaze_estimator.py
threshold_x = 3  # Horizontal sensitivity
threshold_y = 3  # Vertical sensitivity
```

**Phone Detection:**
```python
# In utils/object_detector.py
confidence_threshold = 0.25  # 25% confidence
```

**Looking Away:**
```python
# In pro_interview_system.py
looking_away_frames = 25  # ~0.8 seconds
```

## 📁 Project Structure

```
openface_interviewer/
├── pro_interview_system.py    # Main application
├── utils/
│   ├── face_tracker.py        # Face detection
│   ├── gaze_estimator.py      # Gaze tracking
│   ├── object_detector.py     # YOLO detection
│   ├── behavior_analyzer.py   # Behavior analysis
│   └── risk_model.py          # Risk scoring
├── models/                     # AI models
├── evidence/                   # Screenshots
└── reports/                    # JSON reports
```

## 🎯 Detection Methods

### Eye Gaze Tracking
- **Method:** Iris position detection
- **Accuracy:** 90%+
- **FPS:** 30
- **Latency:** <50ms

### Phone Detection
- **Model:** YOLOv8n
- **Classes:** phone, tablet, laptop, book
- **Confidence:** 25%
- **Speed:** Real-time

### Behavior Analysis
- **Blink detection**
- **Stress level analysis**
- **Whispering detection**
- **Reading pattern detection**

## 📊 Reports

### Integrity Report Includes:
- Risk score (0-100)
- Total violations
- Violation breakdown
- Attention analysis
- Behavior summary
- Evidence screenshots
- Detailed timeline

### Export Format:
```json
{
  "report_metadata": {...},
  "integrity_score": {...},
  "attention_analysis": {...},
  "behavior_analysis": {...},
  "violation_summary": {...}
}
```

## 🔒 Privacy & Ethics

- **Local Processing:** All data processed locally
- **No Cloud:** No data sent to external servers
- **Consent Required:** Inform candidates before monitoring
- **Data Protection:** Secure storage of evidence
- **Transparency:** Clear violation criteria

## 🐛 Troubleshooting

### Camera Not Working
```bash
python test_camera_simple.py
```

### Low FPS
- Close other applications
- Reduce camera resolution
- Use lighter YOLO model (yolov8n)

### False Positives
- Adjust sensitivity thresholds
- Improve lighting
- Ensure clear camera view

## 📝 Requirements

```
streamlit>=1.28.0
opencv-python>=4.8.0
dlib>=19.24.0
ultralytics>=8.0.0
numpy>=1.24.0
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## 📄 License

MIT License - See LICENSE file

## 👨‍💻 Author

Created for AI-powered interview integrity monitoring

## 🙏 Acknowledgments

- OpenCV for computer vision
- dlib for facial landmarks
- Ultralytics for YOLO
- Streamlit for web interface

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check documentation
- Review troubleshooting guide

---

**⚠️ Disclaimer:** This system is for interview integrity monitoring. Always inform candidates and obtain consent before use. Follow local privacy laws and regulations.
