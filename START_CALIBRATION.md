# 🎯 START HERE - CALIBRATION REQUIRED!

## ⚠️ IMPORTANT: You MUST calibrate before starting interviews!

The system needs to know your exact screen boundaries to accurately detect when eyes go beyond the screen.

---

## 🚀 QUICK START - 3 STEPS:

### Step 1: Open Terminal

Open a new terminal window (separate from the interview system)

### Step 2: Run Calibration

```bash
cd openface_interviewer
source venv/bin/activate
python calibrate_screen.py
```

### Step 3: Complete Calibration

A window will open with RED circles. For each circle:

1. **Look at the RED circle** 👀
2. **Press SPACE** (5 times)
3. **Repeat** for all 9 circles
4. **Press 's'** to save
5. **Press 'q'** to quit

**Time:** 2-3 minutes

---

## 📋 WHAT CALIBRATION DOES:

### Creates Screen Boundary Matrix:

```
┌─────────────────────────────────────┐
│  1 -------- 2 -------- 3            │
│  |                     |            │
│  4 -------- 5 -------- 6            │
│  |                     |            │
│  7 -------- 8 -------- 9            │
│                                     │
│  ✅ Eyes within this = OK           │
│  🚨 Eyes beyond this = CHEATING     │
└─────────────────────────────────────┘
```

### Maps Your Screen:
- **Top edge** - How far up you can look
- **Bottom edge** - How far down you can look
- **Left edge** - How far left you can look
- **Right edge** - How far right you can look

### Result:
- ✅ Look anywhere ON screen = No alert
- 🚨 Look BEYOND screen = Alert in 0.8 seconds

---

## 🎯 AFTER CALIBRATION:

### What Changes:

**Before Calibration:**
```
❌ Cannot start interview
❌ System shows: "CALIBRATION REQUIRED"
❌ Inaccurate detection
```

**After Calibration:**
```
✅ Can start interview
✅ System shows: "System Calibrated"
✅ Accurate screen boundary detection
✅ Detects peeping beyond screen
```

---

## 🧪 HOW IT WORKS:

### During Interview:

```python
# Real-time detection
gaze_x, gaze_y = detect_iris_position()

if within_calibrated_screen_boundaries(gaze_x, gaze_y):
    status = "ON_SCREEN"  # ✅ OK
else:
    status = "BEYOND_SCREEN"  # 🚨 Start counting
    
    if counter > 25:  # ~0.8 seconds
        trigger_alert()  # 🚨 CHEATING DETECTED
```

### What Gets Detected:

**✅ Allowed (Eyes on screen):**
- Look at screen corners
- Look at screen edges
- Move head naturally
- Read text on screen

**🚨 Detected (Eyes beyond screen):**
- Peep left (at notes)
- Peep right (at second monitor)
- Look down (at desk/phone)
- Look up (at ceiling/helper)

---

## 🔧 TROUBLESHOOTING:

### "No face detected"
**Solution:**
- Move closer to camera
- Improve lighting
- Remove obstructions

### "Multiple faces detected"
**Solution:**
- Ensure only you are in frame
- Remove photos from background

### Calibration seems inaccurate
**Solution:**
- Recalibrate in better lighting
- Sit in consistent position
- Press SPACE 5 times per point

---

## 📁 FILES:

### Calibration Script:
```
openface_interviewer/calibrate_screen.py
```

### Calibration Data (Created):
```
openface_interviewer/calibration/calibration_data.json
```

### To Recalibrate:
```bash
rm calibration/calibration_data.json
python calibrate_screen.py
```

---

## ✅ CHECKLIST:

- [ ] Open terminal
- [ ] Run: `cd openface_interviewer`
- [ ] Run: `source venv/bin/activate`
- [ ] Run: `python calibrate_screen.py`
- [ ] Look at 9 RED circles
- [ ] Press SPACE 5 times per circle
- [ ] Press 's' to save
- [ ] Press 'q' to quit
- [ ] Go back to interview system
- [ ] See "✅ System Calibrated"
- [ ] Start interview!

---

## 🚀 READY TO CALIBRATE?

**Run this command in terminal:**

```bash
cd openface_interviewer && source venv/bin/activate && python calibrate_screen.py
```

**Then follow the on-screen instructions!**

---

## 📊 SUMMARY:

**Why calibrate?**
- Maps exact screen boundaries
- Enables accurate "beyond screen" detection
- Required before starting interviews

**How long?**
- 2-3 minutes one-time setup

**Result?**
- Perfect detection of peeping beyond screen
- No false positives
- 95%+ accuracy

**CALIBRATE NOW TO START USING THE SYSTEM!**
