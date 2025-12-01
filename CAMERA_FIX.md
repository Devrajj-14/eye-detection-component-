# 📹 Camera Access Fix

## Issue
"Camera error" or "Camera not accessible" when starting interview

## Solution (macOS)

### Step 1: Grant Camera Permissions

1. **Open System Settings**
   - Click Apple menu > System Settings

2. **Go to Privacy & Security**
   - Click "Privacy & Security" in sidebar

3. **Select Camera**
   - Click "Camera" in the list

4. **Enable for Terminal/Python**
   - Find "Terminal" or "Python" in the list
   - Toggle it ON ✅

### Step 2: Restart Application

```bash
# Stop current app (Ctrl+C)
# Then restart:
streamlit run pro_interview_system.py
```

### Step 3: Test Camera

The camera should now work when you start an interview.

## Alternative Solutions

### Try Different Camera Index

If you have multiple cameras:

```python
# Edit pro_interview_system.py
# Line ~420, change:
cap = cv2.VideoCapture(0)  # Try 0, 1, 2, etc.
```

### Check Camera in Use

```bash
# See if another app is using camera
lsof | grep "AppleCamera"

# Close other apps using camera:
# - Zoom
# - FaceTime
# - Photo Booth
# - Other video apps
```

### Test Camera Separately

```bash
# Quick camera test
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAIL'); cap.release()"
```

## Common Issues

### "Camera not found"
- **Cause**: No camera connected
- **Fix**: Connect USB camera or use built-in camera

### "Permission denied"
- **Cause**: Camera permissions not granted
- **Fix**: Follow Step 1 above

### "Camera in use"
- **Cause**: Another app using camera
- **Fix**: Close other video apps

### "Camera timeout"
- **Cause**: Camera initialization slow
- **Fix**: Wait a few seconds, try again

## Verification

After fixing, you should see:
- ✅ Camera feed appears
- ✅ Face detection works
- ✅ No error messages
- ✅ FPS counter shows ~15-30

## Still Not Working?

### Check System
```bash
# Check camera devices
system_profiler SPCameraDataType

# Check permissions
tccutil reset Camera
```

### Use Test Script
```bash
# Create test file
cat > test_camera.py << 'EOF'
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("✅ Camera accessible")
    ret, frame = cap.read()
    if ret:
        print(f"✅ Frame captured: {frame.shape}")
    else:
        print("❌ Cannot read frame")
else:
    print("❌ Camera not accessible")
cap.release()
EOF

# Run test
python3 test_camera.py
```

## Quick Fix Commands

```bash
# 1. Stop app
# Press Ctrl+C

# 2. Grant permissions (manual in System Settings)

# 3. Restart app
streamlit run pro_interview_system.py

# 4. Start interview and test
```

---

**Most Common Fix**: Grant camera permissions in System Settings > Privacy & Security > Camera
