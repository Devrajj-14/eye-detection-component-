# 🚀 Deployment Instructions

## Quick Fix for Your Current Error

Your deployment is failing because **dlib requires CMake**. Here's the immediate fix:

### For Streamlit Cloud (Easiest)

1. **Replace requirements.txt:**
   ```bash
   # In your repository root
   mv requirements.txt requirements-full.txt
   cp requirements-deploy.txt requirements.txt
   ```

2. **Commit and push:**
   ```bash
   git add .
   git commit -m "Fix: Use deployment-friendly requirements"
   git push
   ```

3. **Redeploy** - Your app should now deploy successfully!

---

## Deployment Options

### Option 1: Streamlit Cloud (Free, No dlib)

**Pros:** Free, easy, automatic deployments
**Cons:** No dlib support (face landmarks disabled)

**Steps:**
1. Fork/push your repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set main file: `pro_interview_system.py`
5. Use `requirements-deploy.txt` as requirements file
6. Deploy!

**Files needed:**
- `requirements-deploy.txt` ✅ (created)
- `packages.txt` ✅ (created)
- `.streamlit/config.toml` ✅ (created)

---

### Option 2: Docker Deployment (Full Features)

**Pros:** All features work, portable
**Cons:** Requires Docker knowledge

**Using Backend API:**
```bash
cd backend
docker build -t interview-api .
docker run -p 8000:8000 interview-api
```

**Using Microservice:**
```bash
cd microservice
docker-compose up
```

Access at: `http://localhost:8000/docs`

---

### Option 3: Render (Full Features)

**Pros:** Free tier, supports CMake
**Cons:** Slower cold starts

**Steps:**
1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: interview-system
    env: python
    buildCommand: |
      apt-get update && apt-get install -y cmake build-essential
      pip install -r requirements.txt
    startCommand: streamlit run pro_interview_system.py --server.port $PORT
```

2. Connect to Render
3. Deploy!

---

### Option 4: Railway (Docker)

**Pros:** Easy Docker deployment
**Cons:** Paid after trial

**Steps:**
1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Deploy: `railway up`

Use the Dockerfile in `backend/` or `microservice/`

---

### Option 5: Heroku (With Buildpacks)

**Pros:** Popular platform
**Cons:** Requires buildpack configuration

**Steps:**
1. Create `Procfile`:
```
web: streamlit run pro_interview_system.py --server.port $PORT
```

2. Create `runtime.txt`:
```
python-3.11
```

3. Deploy:
```bash
heroku create your-app-name
heroku buildpacks:add --index 1 heroku-community/apt
git push heroku main
```

---

## Files Overview

### Created for Deployment:

1. **requirements-deploy.txt** - Cloud-friendly (no dlib)
2. **requirements-light.txt** - Minimal version
3. **packages.txt** - System dependencies for Streamlit Cloud
4. **apt.txt** - Alternative system packages
5. **.streamlit/config.toml** - Streamlit configuration

### Original Files:

- **requirements.txt** - Full version (local development)
- **backend/** - FastAPI microservice (Docker-ready)
- **microservice/** - Advanced microservice (Docker-ready)

---

## Feature Comparison

| Feature | Local (Full) | Cloud (No dlib) | Docker |
|---------|-------------|-----------------|--------|
| Object Detection | ✅ | ✅ | ✅ |
| Gaze Tracking | ✅ | ⚠️ Basic | ✅ |
| Face Landmarks | ✅ | ❌ | ✅ |
| Behavior Analysis | ✅ | ✅ | ✅ |
| Risk Scoring | ✅ | ✅ | ✅ |
| Evidence Capture | ✅ | ✅ | ✅ |

---

## Troubleshooting

### Error: "CMake is not installed"
**Solution:** Use `requirements-deploy.txt` instead of `requirements.txt`

### Error: "Memory limit exceeded"
**Solution:** Use `requirements-light.txt` for minimal memory usage

### Error: "Module not found"
**Solution:** Ensure all files are committed to git:
```bash
git add requirements-deploy.txt packages.txt .streamlit/
git commit -m "Add deployment files"
git push
```

### Error: "Port already in use"
**Solution:** 
- Streamlit Cloud: Automatic
- Local: Use `--server.port 8502`
- Docker: Change port mapping `-p 8080:8501`

---

## Recommended Setup

### For Quick Demo (5 minutes):
→ **Streamlit Cloud** with `requirements-deploy.txt`

### For Production (Full Features):
→ **Docker** with `backend/` or `microservice/`

### For Development:
→ **Local** with full `requirements.txt`

---

## Environment Variables

Set these in your deployment platform:

```bash
# Optional
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

---

## Next Steps

1. ✅ Choose deployment platform
2. ✅ Use appropriate requirements file
3. ✅ Deploy
4. ✅ Test the application
5. ✅ Monitor logs for errors

---

## Support

If deployment still fails:
1. Check platform logs
2. Verify all files are committed
3. Try Docker deployment (always works)
4. Use `requirements-light.txt` for minimal setup

---

## Quick Commands

**Test locally without dlib:**
```bash
pip install -r requirements-deploy.txt
streamlit run pro_interview_system.py
```

**Test with Docker:**
```bash
cd backend
docker build -t test .
docker run -p 8000:8000 test
```

**Deploy to Streamlit Cloud:**
```bash
git add requirements-deploy.txt packages.txt
git commit -m "Deploy config"
git push
# Then connect on share.streamlit.io
```

Good luck with your deployment! 🚀
