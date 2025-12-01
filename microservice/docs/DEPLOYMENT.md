# 🚀 Deployment Guide

## Quick Start

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Download models
python download_models.py

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Docker (Recommended)

```bash
# Build image
docker build -t ai-interview-api:latest .

# Run container
docker run -p 8000:8000 ai-interview-api:latest

# Or use docker-compose
docker-compose up
```

### 3. Test API

```bash
curl http://localhost:8000/health
```

---

## Production Deployment

### Option 1: Docker Compose

**Best for:** Single server deployment

```bash
# Production compose file
docker-compose -f docker-compose.prod.yml up -d
```

**Features:**
- Auto-restart
- Resource limits
- Redis for sessions
- Health checks

### Option 2: Kubernetes

**Best for:** Scalable cloud deployment

```bash
# Apply deployment
kubectl apply -f k8s/deployment.yaml

# Apply service
kubectl apply -f k8s/service.yaml

# Apply HPA (auto-scaling)
kubectl apply -f k8s/hpa.yaml
```

**Features:**
- Horizontal auto-scaling
- Load balancing
- Rolling updates
- Health monitoring

### Option 3: Cloud Run (Serverless)

**Best for:** Serverless, pay-per-use

```bash
# Deploy to Google Cloud Run
gcloud run deploy ai-interview-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300
```

**Features:**
- Auto-scaling to zero
- Pay per request
- HTTPS by default
- Global CDN

### Option 4: AWS ECS

**Best for:** AWS infrastructure

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker build -t ai-interview-api .
docker tag ai-interview-api:latest <account>.dkr.ecr.us-east-1.amazonaws.com/ai-interview-api:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/ai-interview-api:latest

# Deploy to ECS
aws ecs update-service --cluster interview-cluster --service api-service --force-new-deployment
```

---

## Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info

# Model Configuration
MODEL_PATH=/app/models
YOLO_MODEL=yolov8n.pt
CONFIDENCE_THRESHOLD=0.25

# Session Configuration
SESSION_EXPIRE_SECONDS=900
USE_REDIS=false
REDIS_URL=redis://localhost:6379

# Performance
WORKERS=1
MAX_CONCURRENT_SESSIONS=10
```

---

## Scaling Strategies

### Horizontal Scaling

**Load Balancer + Multiple Instances**

```
┌─────────────┐
│Load Balancer│
└──────┬──────┘
       │
   ┌───┴───┬───────┬───────┐
   │       │       │       │
┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌──▼──┐
│API 1│ │API 2│ │API 3│ │API 4│
└─────┘ └─────┘ └─────┘ └─────┘
```

**Kubernetes HPA:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-interview-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Vertical Scaling

**Increase resources per instance**

```yaml
resources:
  requests:
    memory: "2Gi"
    cpu: "1"
  limits:
    memory: "4Gi"
    cpu: "2"
```

### GPU Acceleration

**For faster inference**

```dockerfile
# Use CUDA base image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install PyTorch with CUDA
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**Kubernetes GPU node:**
```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

---

## Monitoring

### Health Checks

```bash
# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

# Readiness probe
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Prometheus Metrics

```python
# Add to main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Security

### API Key Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = "your-secret-key"
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```

### HTTPS/TLS

```bash
# Use reverse proxy (nginx)
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
    }
}
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/analyze-frame")
@limiter.limit("10/minute")
async def analyze_frame(request: Request, ...):
    ...
```

---

## Performance Optimization

### Model Warmup

```python
@app.on_event("startup")
async def warmup():
    # Run dummy inference
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    await frame_processor.process_frame(dummy_frame)
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_model():
    return YOLO('yolov8n.pt')
```

### Async Processing

```python
import asyncio

async def process_batch(frames):
    tasks = [process_frame(f) for f in frames]
    return await asyncio.gather(*tasks)
```

---

## Troubleshooting

### High Memory Usage

```bash
# Reduce model size
YOLO_MODEL=yolov8n.pt  # Use nano model

# Limit concurrent sessions
MAX_CONCURRENT_SESSIONS=5
```

### Slow Response Times

```bash
# Use GPU
docker run --gpus all -p 8000:8000 ai-interview-api

# Reduce image resolution
# Process at 640x480 instead of 1920x1080
```

### Connection Timeouts

```bash
# Increase timeout
uvicorn main:app --timeout-keep-alive 300
```

---

## Backup & Recovery

### Session Data Backup

```bash
# Backup Redis data
redis-cli --rdb /backup/dump.rdb

# Restore
redis-cli --rdb /backup/dump.rdb
```

### Model Versioning

```bash
# Tag models
models/
├── yolov8n-v1.0.pt
├── yolov8n-v1.1.pt
└── current -> yolov8n-v1.1.pt
```

---

## Cost Optimization

### Cloud Run (Serverless)

- **Cost:** ~$0.10 per 1000 requests
- **Scaling:** Auto-scales to zero
- **Best for:** Variable traffic

### ECS/EKS (Container)

- **Cost:** ~$50-200/month per instance
- **Scaling:** Manual or auto
- **Best for:** Consistent traffic

### Self-Hosted

- **Cost:** Server costs only
- **Scaling:** Manual
- **Best for:** High volume, cost-sensitive

---

## Next Steps

1. ✅ Deploy to staging environment
2. ✅ Run load tests
3. ✅ Configure monitoring
4. ✅ Set up CI/CD pipeline
5. ✅ Deploy to production
6. ✅ Monitor and optimize

**Your microservice is production-ready!** 🚀
