# 🚀 QUICK START - Screen Boundary Tracking

## 🎯 What This Does

**Tracks your ENTIRE screen** and only alerts when eyes go **BEYOND screen edges**.

- ✅ Look anywhere ON screen = OK
- ✅ Move head naturally = OK  
- 🚨 Look OFF screen (notes/phone) = ALERT

---

## ⚡ 3-Step Setup

### 1️⃣ Run Calibration (2 minutes)

```bash
cd openface_interviewer
source venv/bin/activate
python calibrate_screen.py
```

**What to do:**
- Look at 9 RED circles that appear
- Press SPACE for each circle (5 times)
- Press 's' to save when done

### 2️⃣ Test It (Optional)

```bash
python test_calibration.py
```

**Test these:**
- Look at screen corners → Should say "ON SCREEN" ✅
- Look at desk/notes → Should say "OFF SCREEN" 🚨

### 3️⃣ Start Interview

```bash
streamlit run pro_interview_system.py
```

Open: **http://localhost:8502**

---

## ✅ What's Allowed (No Alerts)

```
✅ Turn head left/right while eyes on screen
✅ Look at any corner of screen
✅ Look at any edge of screen
✅ Move head naturally
✅ Adjust posture
✅ Read text on screen
✅ Blink normally
```

## 🚨 What Triggers Alerts (Cheating)

```
🚨 Look down at desk/notes
🚨 Look at phone
🚨 Look at second monitor
🚨 Look away from screen
🚨 Look at someone helping you
```

---

## 📊 How It Works

### Before Calibration:
```
❌ Head movement → False alerts
❌ Looking at screen edges → False alerts
❌ Natural movement → False alerts
```

### After Calibration:
```
✅ Head movement + eyes on screen → No alerts
✅ Looking at screen edges → No alerts
✅ Natural movement → No alerts
🚨 Eyes OFF screen → Alert (accurate detection)
```

---

## 🔧 Troubleshooting

### "No calibration found"
**Solution:** Run `python calibrate_screen.py` first

### "No face detected" during calibration
**Solution:** 
- Move closer to camera
- Improve lighting
- Remove obstructions

### Calibration seems inaccurate
**Solution:**
- Recalibrate in better lighting
- Sit in consistent position
- Capture more samples per point

### Want to recalibrate
**Solution:**
```bash
rm calibration/calibration_data.json
python calibrate_screen.py
```

---

## 📁 Files

- `calibrate_screen.py` - Run calibration
- `test_calibration.py` - Test accuracy
- `pro_interview_system.py` - Main interview system
- `calibration/calibration_data.json` - Your calibration data

---

## 🎉 That's It!

**Calibrate once, use forever** (until you change position/monitor).

System now tracks your ENTIRE screen and only alerts when eyes go beyond it!
