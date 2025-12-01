# 🎯 Screen Calibration Guide

## Why Calibrate?

Calibration teaches the system **exactly where your screen boundaries are** by mapping your eye gaze to screen coordinates. This allows the system to:

✅ **Allow head movement** - You can move your head naturally as long as eyes stay on screen
✅ **Detect off-screen gaze** - System knows when eyes look beyond screen edges
✅ **Reduce false positives** - No alerts for natural head movements
✅ **Improve accuracy** - Personalized to your sitting position and screen

## Quick Start

### Step 1: Run Calibration

```bash
cd openface_interviewer
source venv/bin/activate
python calibrate_screen.py
```

### Step 2: Follow Instructions

1. **Position yourself** - Sit in your normal interview position
2. **Look at RED circles** - 9 points will appear on screen
3. **Press SPACE** - Capture 5 samples per point (keep looking at circle)
4. **Repeat** - Do this for all 9 points
5. **Press 's'** - Save calibration when complete

### Step 3: Start Interview

```bash
streamlit run pro_interview_system.py
```

The system will automatically load your calibration!

## Calibration Points

The system uses **9-point calibration** covering the entire screen:

```
1 -------- 2 -------- 3
|                     |
|                     |
4 -------- 5 -------- 6
|                     |
|                     |
7 -------- 8 -------- 9
```

This maps:
- **Corners** (1, 3, 7, 9) - Extreme screen edges
- **Edges** (2, 4, 6, 8) - Mid-points
- **Center** (5) - Screen center

## What Gets Calibrated?

### Screen Boundaries
- **Left edge** - How far left you can look while on screen
- **Right edge** - How far right you can look while on screen
- **Top edge** - How far up you can look while on screen
- **Bottom edge** - How far down you can look while on screen

### Gaze Ranges
- **Horizontal gaze range** - Left-right eye movement limits
- **Vertical gaze range** - Up-down eye movement limits
- **Head pose range** - Natural head movement while looking at screen

## How It Works

### Before Calibration (Uncalibrated Mode)
```
❌ Head turn 20° → FALSE ALERT
❌ Look at screen edge → FALSE ALERT
❌ Natural movement → FALSE ALERT
```

### After Calibration (Calibrated Mode)
```
✅ Head turn 20° + eyes on screen → NO ALERT
✅ Look at screen edges → NO ALERT
✅ Natural movement → NO ALERT
🚨 Eyes look OFF screen → ALERT (cheating detected)
```

## Detection Logic

### With Calibration:
```python
if eyes_within_screen_bounds:
    status = "ON_SCREEN"  # ✅ OK
else:
    status = "OFF_SCREEN"  # 🚨 CHEATING
```

### Without Calibration:
```python
if gaze_deviation > threshold:
    status = "LOOKING_AWAY"  # ⚠️ May be false positive
```

## Tips for Best Results

### 1. Consistent Position
- Sit in the **same position** for calibration and interview
- Keep **same distance** from screen
- Use **same chair height**

### 2. Good Lighting
- Ensure **face is well-lit**
- Avoid **backlighting** (window behind you)
- Use **consistent lighting** for calibration and interview

### 3. Clear View
- **Remove glasses** if they cause reflections
- Ensure **camera can see both eyes**
- Keep **hair away from eyes**

### 4. Multiple Samples
- The system captures **5 samples per point**
- Keep looking at the circle while pressing SPACE
- Don't rush - take your time

### 5. Recalibrate When Needed
- If you **change position**
- If you **adjust monitor**
- If you **change lighting**
- If accuracy seems off

## Calibration Files

### Location
```
openface_interviewer/
└── calibration/
    └── calibration_data.json
```

### Contents
```json
{
  "timestamp": "2024-12-02T10:30:00",
  "screen_bounds": {
    "gaze_x_min": -8.5,
    "gaze_x_max": 8.5,
    "gaze_y_min": -6.2,
    "gaze_y_max": 6.2,
    "head_yaw_range": [-15, 15],
    "head_pitch_range": [-10, 10]
  },
  "num_samples": 45
}
```

## Troubleshooting

### "No face detected"
- **Move closer** to camera
- **Improve lighting**
- **Remove obstructions** (hair, glasses)

### "Multiple faces detected"
- **Ensure only you** are in frame
- **Remove photos/posters** from background

### "No landmarks detected"
- **Face camera directly**
- **Improve lighting**
- **Check camera quality**

### Calibration seems inaccurate
- **Recalibrate** in better lighting
- **Ensure consistent position**
- **Capture more samples** (press SPACE multiple times per point)

## Advanced: Manual Calibration Adjustment

If you need to adjust calibration manually, edit `calibration/calibration_data.json`:

```json
{
  "screen_bounds": {
    "gaze_x_min": -10,  // Increase for wider left range
    "gaze_x_max": 10,   // Increase for wider right range
    "gaze_y_min": -8,   // Increase for wider up range
    "gaze_y_max": 8     // Increase for wider down range
  }
}
```

**Larger values** = More permissive (less sensitive)
**Smaller values** = More strict (more sensitive)

## Testing Calibration

After calibration, test it:

1. **Look at screen corners** → Should be "ON_SCREEN"
2. **Look just beyond screen** → Should be "OFF_SCREEN"
3. **Move head while looking at screen** → Should stay "ON_SCREEN"
4. **Look at desk/notes** → Should be "OFF_SCREEN"

## Recalibration

To recalibrate:

```bash
# Delete old calibration
rm calibration/calibration_data.json

# Run calibration again
python calibrate_screen.py
```

## Integration with Interview System

The interview system automatically:
1. **Loads calibration** on startup
2. **Uses calibrated boundaries** for detection
3. **Falls back** to uncalibrated mode if no calibration found
4. **Shows calibration status** in UI

### Calibration Status

**✅ Calibrated Mode:**
- More accurate detection
- Allows natural head movement
- Faster detection (1 second)
- Higher confidence

**⚠️ Uncalibrated Mode:**
- Conservative detection
- May have false positives
- Slower detection (2 seconds)
- Lower confidence

---

## Summary

1. **Run calibration** before first interview
2. **Look at 9 points** and press SPACE
3. **Save calibration** when complete
4. **Start interview** - calibration loads automatically
5. **Recalibrate** if position/lighting changes

**Calibration takes 2-3 minutes but dramatically improves accuracy!**
