# 🎯 AI Interview Integrity Backend Service

FastAPI microservice for real-time cheating detection in online interviews.

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Build image
docker build -t interview-api .

# Run container
docker run -p 8000:8000 interview-api

# Test
curl http://localhost:8000/health
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create models directory
mkdir -p models

# Download YOLO model (optional)
# Place yolov8n.pt in models/ directory

# Run server
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### POST /start-session

Start a new interview session.

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
  "message": "Session started successfully",
  "timestamp": 1701234567.89
}
```

### POST /analyze-frame

Analyze a single frame for cheating detection.

**Request:**
```json
{
  "session_id": "uuid",
  "frame": "<base64_encoded_image>"
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
  "events": []
}
```

### POST /end-session

End session and get final verdict.

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
  "duration_seconds": 1234.5
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "ai-interview-monitor",
  "models_loaded": true,
  "active_sessions": 5
}
```

## 📊 Detection Features

- **Face Detection** - MediaPipe face detection
- **Gaze Tracking** - Iris-based gaze estimation
- **Multi-Person Detection** - Detects multiple faces
- **Object Detection** - YOLO-based phone/book detection
- **Risk Scoring** - Real-time risk calculation with decay
- **Behavior Analysis** - Attention and stress monitoring

## 🎯 Events Detected

| Event | Risk Increase | Description |
|-------|---------------|-------------|
| PHONE_DETECTED | +30 | Phone detected in frame |
| MULTIPLE_FACES | +25 | Multiple people detected |
| EYES_OFF_SCREEN | +15 | Eyes looking away |
| LOOKING_AWAY | +10 | Gaze not centered |
| NO_FACE | +20 | No face detected |
| SUSPICIOUS_OBJECT | +15 | Book/paper detected |

## 🔧 Configuration

### Environment Variables

```bash
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
```

### Model Files

Place model files in `models/` directory:
- `yolov8n.pt` - YOLO model (optional, will download automatically)

## 📈 Performance

- **Latency:** < 150ms per frame
- **Throughput:** 10+ concurrent sessions
- **Memory:** ~2GB RAM
- **CPU:** Optimized for CPU-only inference

## 🐛 Troubleshooting

### Models not loading

```bash
# Ensure models directory exists
mkdir -p models

# YOLO will auto-download on first use
```

### High memory usage

```bash
# Reduce concurrent sessions
# Use smaller YOLO model (yolov8n)
```

### Slow processing

```bash
# Reduce image resolution before sending
# Use GPU version of PyTorch if available
```

## 📝 Example Client (Python)

```python
import requests
import base64
import cv2

# Start session
response = requests.post('http://localhost:8000/start-session', json={
    'candidate_id': 'test_123'
})
session_id = response.json()['session_id']

# Capture frame
cap = cv2.VideoCapture(0)
ret, frame = cap.read()

# Encode to base64
_, buffer = cv2.imencode('.jpg', frame)
frame_b64 = base64.b64encode(buffer).decode('utf-8')

# Analyze frame
response = requests.post('http://localhost:8000/analyze-frame', json={
    'session_id': session_id,
    'frame': frame_b64
})
result = response.json()
print(f"Risk: {result['risk_score']}, Cheating: {result['cheating']}")

# End session
response = requests.post('http://localhost:8000/end-session', json={
    'session_id': session_id
})
final = response.json()
print(f"Verdict: {final['verdict']}")
```

## 🚀 Deployment

### Render.com

1. Create new Web Service
2. Connect GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
    restart: unless-stopped
```

## 📄 License

MIT License

---

**API Documentation:** http://localhost:8000/docs
**Health Check:** http://localhost:8000/health
