# Deployment Fix Guide

## Problem
The project fails to deploy because `dlib` requires CMake to compile, which is not available in most cloud deployment environments.

## Solutions

### Option 1: Deploy Without dlib (Recommended for Cloud)

Use the lightweight requirements file that excludes dlib:

**For Streamlit Cloud:**
1. Rename `requirements-deploy.txt` to `requirements.txt`
2. Add `packages.txt` file (already created)
3. Deploy normally

**For Render/Railway/Heroku:**
1. Use `requirements-deploy.txt` instead of `requirements.txt`
2. Set build command: `pip install -r requirements-deploy.txt`

### Option 2: Use Docker (Best for Full Features)

Deploy using Docker which can install CMake:

```bash
cd backend  # or microservice
docker build -t interview-system .
docker run -p 8000:8000 interview-system
```

### Option 3: Add System Dependencies

**For Streamlit Cloud:**
Create `packages.txt` (already created) with:
```
cmake
build-essential
libopenblas-dev
liblapack-dev
```

**For Render:**
Add to `render.yaml`:
```yaml
services:
  - type: web
    name: interview-system
    env: python
    buildCommand: |
      apt-get update
      apt-get install -y cmake build-essential
      pip install -r requirements.txt
    startCommand: streamlit run pro_interview_system.py
```

### Option 4: Modify Code to Make dlib Optional

The code has been updated to gracefully handle missing dlib:

```python
try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError:
    DLIB_AVAILABLE = False
    print("Warning: dlib not available. Face landmark detection disabled.")
```

## Quick Fix for Current Deployment

**Step 1:** Rename files
```bash
cd openface_interviewer
mv requirements.txt requirements-full.txt
mv requirements-deploy.txt requirements.txt
```

**Step 2:** Redeploy

The system will work with reduced functionality:
- ✅ Object detection (YOLO)
- ✅ Gaze estimation (basic)
- ✅ Behavior analysis
- ❌ Face landmarks (requires dlib)
- ❌ Precise facial feature tracking

## Recommended Deployment Platforms

### 1. Docker (Full Features)
- ✅ All features work
- ✅ Easy to deploy
- Use: `backend/` or `microservice/` folders

### 2. Streamlit Cloud (Limited)
- ✅ Free hosting
- ⚠️ No dlib support
- Use: `requirements-deploy.txt`

### 3. Render (Full Features with setup)
- ✅ Can install CMake
- ✅ All features work
- Use: Custom build command

### 4. Railway (Full Features)
- ✅ Docker support
- ✅ All features work
- Use: Dockerfile

## Files Created

1. `requirements-light.txt` - Minimal dependencies
2. `requirements-deploy.txt` - No dlib, optimized for cloud
3. `packages.txt` - System packages for Streamlit Cloud
4. `apt.txt` - Alternative system packages file

## Testing Locally Without dlib

```bash
pip install -r requirements-deploy.txt
streamlit run pro_interview_system.py
```

The system will automatically detect missing dlib and disable related features.
