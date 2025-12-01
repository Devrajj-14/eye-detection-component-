# 🎯 AI Interview Integrity Microservice

Production-ready REST API for real-time cheating detection in online interviews.

## 🚀 Quick Start

```bash
# 1. Build Docker image
docker build -t ai-interview-api .

# 2. Run container
docker run -p 8000:8000 ai-interview-api

# 3. Test API
curl http://localhost:8000/health
```

**API is now running at:** `http://localhost:8000`

---

## 📋 Features

### Core Detection
- ✅ **Gaze Tracking** - Iris-based eye tracking
- ✅ **Face Detection** - Multi-person detection
- ✅ **Object Detection** - Phone, tablet, book detection (including partial)
- ✅ **Behavior Analysis** - Stress, whispering, reading patterns
- ✅ **Risk Scoring** - Real-time risk calculation with decay

### API Features
- ✅ **REST Endpoints** - Simple HTTP API
- ✅ **WebSocket Streaming** - Real-time frame processing
- ✅ **Session Management** - Auto-expiry (15 min)
- ✅ **Stateless Design** - Horizontally scalable
- ✅ **< 70ms Latency** - Fast processing
- ✅ **10+ Concurrent Sessions** - High throughput

---

## 📡 API Endpoints

### POST /start-session
Start a new interview session

**Request:**
```json
{
  "candidate_id": "12345",
  "metadata": {}
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "message": "Session started",
  "timestamp": 1701234567.89
}
```

### POST /analyze-frame
Analyze a single frame

**Request:**
```json
{
  "session_id": "uuid",
  "frame": "<base64_image>",
  "timestamp": 1701234567.89
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "cheating": false,
  "risk_score": 15,
  "attention": 85,
  "gaze": "center",
  "faces": 1,
  "objects": [],
  "events": [],
  "processing_time_ms": 45.2,
  "timestamp": 1701234567.89
}
```

### POST /end-session
End session and get final verdict

**Request:**
```json
{
  "session_id": "uuid"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "final_risk_score": 84,
  "verdict": "CHEATING",
  "total_violations": 12,
  "duration_seconds": 1234.5,
  "summary": {...}
}
```

### GET /health
Health check

**Response:**
```json
{
  "status": "ok",
  "service": "ai-interview-monitor",
  "uptime_seconds": 3600,
  "active_sessions": 5,
  "models_loaded": true
}
```

### WS /ws/stream
WebSocket streaming endpoint

**Messages:**
```json
// Start session
{"action": "start", "candidate_id": "12345"}

// Send frame
{"action": "frame", "frame": "<base64>"}

// End session
{"action": "end"}
```

---

## 🔧 Installation

### Option 1: Docker (Recommended)

```bash
docker-compose up
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Download models
mkdir -p models
wget -O models/shape_predictor_68_face_landmarks.dat.bz2 \
  http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bzip2 -d models/shape_predictor_68_face_landmarks.dat.bz2

# Run server
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 💻 Client Examples

### Python

```python
from clients.python_client import InterviewClient

client = InterviewClient("http://localhost:8000")
session_id = client.start_session("candidate_123")

# Analyze frame
result = client.analyze_frame_from_array(session_id, frame)
print(f"Risk: {result['risk_score']}")

# End session
final = client.end_session(session_id)
print(f"Verdict: {final['verdict']}")
```

### JavaScript

```javascript
const client = new InterviewClient('http://localhost:8000');

// Start session
const sessionId = await client.startSession('candidate_123');

// Analyze frame from canvas
const result = await client.analyzeFrameFromCanvas(sessionId, canvas);
console.log('Risk:', result.risk_score);

// End session
const final = await client.endSession(sessionId);
console.log('Verdict:', final.verdict);
```

### React

```jsx
import InterviewMonitor from './clients/react_example';

function App() {
  return (
    <InterviewMonitor 
      apiUrl="http://localhost:8000"
      candidateId="candidate_123"
    />
  );
}
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│         FastAPI Microservice            │
├─────────────────────────────────────────┤
│  Endpoints:                             │
│  - POST /analyze-frame                  │
│  - POST /start-session                  │
│  - POST /end-session                    │
│  - GET /health                          │
│  - WS /ws/stream                        │
├─────────────────────────────────────────┤
│  Frame Processor                        │
│  ├─ Face Detection (dlib)               │
│  ├─ Gaze Tracking (iris-based)          │
│  ├─ Object Detection (YOLO)             │
│  └─ Behavior Analysis                   │
├─────────────────────────────────────────┤
│  Risk Engine                            │
│  ├─ Score Calculation                   │
│  ├─ Event Processing                    │
│  └─ Verdict Generation                  │
├─────────────────────────────────────────┤
│  Session Manager                        │
│  ├─ In-Memory / Redis                   │
│  ├─ Auto-expiry (15 min)                │
│  └─ Concurrent sessions                 │
└─────────────────────────────────────────┘
```

---

## 🎯 Detection Events

| Event | Severity | Risk Increase |
|-------|----------|---------------|
| PHONE_DETECTED | Critical | +30 |
| PHONE_PARTIAL_DETECTED | High | +20 |
| MULTIPLE_FACES | Critical | +25 |
| EYES_OFF_SCREEN | High | +15 |
| LOOKING_AWAY | Medium | +10 |
| NO_FACE | High | +20 |
| SUSPICIOUS_OBJECT | Medium | +15 |
| WHISPERING | Medium | +10 |
| READING_PATTERN | Medium | +12 |
| STRESS_HIGH | Low | +5 |

---

## 🚀 Deployment

### Docker Compose

```bash
docker-compose up -d
```

### Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
```

### Cloud Run

```bash
gcloud run deploy ai-interview-api --source .
```

**See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.**

---

## 📈 Performance

- **Latency:** < 70ms per frame
- **Throughput:** 10+ concurrent sessions
- **Scalability:** Horizontal scaling ready
- **GPU Support:** Optional CUDA acceleration

---

## 🔒 Security

- Rate limiting per session
- API key authentication (optional)
- HTTPS/TLS support
- Input validation
- Session timeout (15 min)

---

## 📝 Environment Variables

```bash
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
MODEL_PATH=/app/models
CONFIDENCE_THRESHOLD=0.25
SESSION_EXPIRE_SECONDS=900
USE_REDIS=false
REDIS_URL=redis://localhost:6379
```

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Load testing
locust -f tests/load_test.py
```

---

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Scaling Strategies](docs/SCALING.md)
- [Client Examples](clients/)

---

## 🤝 Integration Examples

### WebRTC Integration

```javascript
// Capture from WebRTC stream
const stream = await navigator.mediaDevices.getUserMedia({ video: true });
const video = document.createElement('video');
video.srcObject = stream;

// Send frames to API
setInterval(async () => {
  const canvas = captureFrame(video);
  const result = await client.analyzeFrameFromCanvas(sessionId, canvas);
  updateUI(result);
}, 1000);
```

### Node.js Server

```javascript
const express = require('express');
const InterviewClient = require('./clients/javascript_client');

const app = express();
const client = new InterviewClient('http://localhost:8000');

app.post('/interview/start', async (req, res) => {
  const sessionId = await client.startSession(req.body.candidateId);
  res.json({ sessionId });
});

app.post('/interview/analyze', async (req, res) => {
  const result = await client.analyzeFrame(req.body.sessionId, req.body.frame);
  res.json(result);
});
```

---

## 🐛 Troubleshooting

### High Memory Usage
```bash
# Use smaller model
YOLO_MODEL=yolov8n.pt

# Limit sessions
MAX_CONCURRENT_SESSIONS=5
```

### Slow Processing
```bash
# Enable GPU
docker run --gpus all -p 8000:8000 ai-interview-api

# Reduce resolution
# Process at 640x480
```

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

- FastAPI for the web framework
- OpenCV for computer vision
- dlib for face detection
- Ultralytics YOLO for object detection

---

## 📞 Support

For issues and questions:
- GitHub Issues
- Documentation
- API Reference

---

**🚀 Your microservice is production-ready!**
