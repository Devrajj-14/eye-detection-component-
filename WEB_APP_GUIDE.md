# Web Application Guide

## 🌐 Running the Web Interface

The OpenFace 3.0 application is now available as a web interface using Streamlit!

### Quick Start

```bash
cd openface_interviewer
source venv/bin/activate
streamlit run app_web.py
```

The app will automatically open in your browser at:
- **Local URL**: http://localhost:8501
- **Network URL**: http://192.168.29.5:8501 (accessible from other devices on your network)

## 🎮 Using the Web Interface

### Main Features

1. **Sidebar Controls**
   - ✅ Start Camera - Toggle camera on/off
   - 📍 Start Calibration - Begin 9-point calibration
   - 🛑 Stop Calibration - Cancel calibration
   - 🔍 Enable Object Detection - Toggle object detection

2. **Live Video Feed**
   - Real-time face tracking
   - Eye gaze visualization
   - Person ID labels
   - Head pose axes
   - FPS counter

3. **Status Panel**
   - Calibration progress
   - Detection status
   - FPS metrics
   - People count

### Step-by-Step Usage

#### 1. Start the Camera
- Click the **"Start Camera"** checkbox in the sidebar
- Grant camera permissions if prompted
- Video feed will appear in the main area

#### 2. Calibrate (Optional but Recommended)
- Click **"Start Calibration"** button
- Look at each red dot that appears (9 total)
- Keep your head still, follow dots with eyes only
- Each dot samples for 1 second
- Status shows "✅ Calibration Complete" when done

#### 3. Enable Object Detection (Optional)
- Check **"Enable Object Detection"** in sidebar
- Objects will be detected and highlighted
- Detected objects auto-saved to `captures/` folder

#### 4. Monitor Statistics
- View real-time FPS
- See number of people detected
- Check calibration status

## 🎨 Interface Layout

```
┌─────────────────────────────────────────────────────────┐
│  👁️ OpenFace 3.0 Multi-Person Tracker                   │
├──────────────────┬──────────────────────────────────────┤
│                  │                                       │
│  Sidebar         │  Live Video Feed                      │
│  Controls:       │  ┌─────────────────────────────┐     │
│  ☐ Start Camera  │  │                             │     │
│  📍 Calibration  │  │   [Video Stream]            │     │
│  🔍 Detection    │  │                             │     │
│                  │  └─────────────────────────────┘     │
│  Status:         │                                       │
│  ✅ Calibrated   │  Information Panel:                   │
│  FPS: 25.3       │  • Features list                      │
│                  │  • Instructions                       │
│                  │  • Statistics                         │
└──────────────────┴──────────────────────────────────────┘
```

## 🔧 Configuration

### Camera Settings
Edit `app_web.py` to change camera resolution:
```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
```

### Port Configuration
Run on a different port:
```bash
streamlit run app_web.py --server.port 8502
```

### Network Access
Access from other devices on your network:
```bash
streamlit run app_web.py --server.address 0.0.0.0
```

## 📊 Features Available

### ✅ Implemented
- [x] Multi-person face tracking
- [x] 68-point facial landmarks
- [x] Head pose estimation
- [x] Eye gaze direction
- [x] Person ID tracking
- [x] 9-point calibration
- [x] Object detection
- [x] Auto-capture
- [x] Real-time FPS display
- [x] Web-based interface
- [x] Responsive controls

### 🎯 Real-Time Overlays
- Green boxes around faces
- Person ID labels
- Facial landmark points
- Head pose axes (RGB)
- Gaze direction arrows (magenta)
- Calibration points (red)
- Object detection boxes (yellow)

## 🚀 Performance Tips

### For Better Performance
1. **Reduce Resolution**: Lower camera resolution in code
2. **Disable Detection**: Turn off object detection when not needed
3. **Good Lighting**: Improves face detection speed
4. **Close Other Apps**: Free up system resources

### Expected Performance
- **FPS**: 15-30 on modern CPU
- **Latency**: <100ms per frame
- **Max People**: 5-10 simultaneous

## 🐛 Troubleshooting

### Camera Not Working
```bash
# Check camera permissions in System Settings
# macOS: System Settings > Privacy & Security > Camera
```

### Port Already in Use
```bash
# Use a different port
streamlit run app_web.py --server.port 8502
```

### Slow Performance
- Reduce camera resolution
- Disable object detection
- Close other applications
- Ensure good lighting

### Browser Not Opening
```bash
# Manually open the URL shown in terminal
# Usually: http://localhost:8501
```

## 📱 Mobile Access

Access from your phone/tablet on the same network:
1. Note the Network URL from terminal output
2. Open browser on mobile device
3. Navigate to the Network URL
4. Use the interface (may be slower on mobile)

## 🔒 Security Notes

### Local Network Only
- By default, accessible only on local network
- No internet connection required
- All processing happens locally

### Camera Privacy
- Camera only active when "Start Camera" is checked
- No video recording or transmission
- All data stays on your device

## 💡 Tips & Tricks

### Best Practices
1. **Calibrate First**: Better gaze accuracy
2. **Good Lighting**: Faster face detection
3. **Stable Camera**: Mount camera if possible
4. **Head Still**: During calibration, keep head still

### Keyboard Shortcuts
- `Ctrl+C` in terminal to stop server
- Refresh browser to restart app
- Use browser zoom for better visibility

## 📝 Comparison: Web vs Desktop

| Feature | Web (Streamlit) | Desktop (PyQt5) |
|---------|----------------|-----------------|
| Installation | ✅ Easy | ✅ Easy |
| Interface | 🌐 Browser | 🖥️ Native |
| Performance | ⚡ Good | ⚡ Better |
| Mobile Access | ✅ Yes | ❌ No |
| Network Access | ✅ Yes | ❌ No |
| Responsiveness | 📱 Responsive | 🖥️ Fixed |

## 🎓 Advanced Usage

### Custom Styling
Edit Streamlit theme in `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#00FF00"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

### Multiple Cameras
Change camera index in code:
```python
cap = cv2.VideoCapture(1)  # Use camera 1 instead of 0
```

### Save Configuration
Streamlit automatically saves widget states between sessions.

## 📞 Support

### Documentation
- Main README: [README.md](README.md)
- Quick Start: [QUICKSTART.md](QUICKSTART.md)
- Full Guide: [USAGE.md](USAGE.md)

### Common Issues
- Camera permissions: Check system settings
- Port conflicts: Use different port
- Performance: Reduce resolution or disable detection

## 🎉 Quick Commands

```bash
# Start web app
streamlit run app_web.py

# Start on different port
streamlit run app_web.py --server.port 8502

# Enable network access
streamlit run app_web.py --server.address 0.0.0.0

# Stop server
# Press Ctrl+C in terminal
```

---

**Web App Status**: ✅ Running
**Access URL**: http://localhost:8501
**Network URL**: Check terminal output
**Status**: Ready to use! 🚀
