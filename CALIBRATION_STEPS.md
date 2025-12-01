# 🎯 CALIBRATION - STEP BY STEP

## ✅ CALIBRATION IS NOW RUNNING!

A window should be open showing your camera with a **RED CIRCLE**.

---

## 📋 STEP-BY-STEP INSTRUCTIONS

### Step 1: Position Yourself
- Sit in your **normal interview position**
- Make sure your **face is visible** in the camera
- Keep your **head relatively still**

### Step 2: Calibrate Each Point

**You'll see 9 RED circles appear one at a time:**

```
Point 1 (Top-Left)     → Point 2 (Top-Center)    → Point 3 (Top-Right)
         ↓                        ↓                         ↓
Point 4 (Middle-Left)  → Point 5 (Center)        → Point 6 (Middle-Right)
         ↓                        ↓                         ↓
Point 7 (Bottom-Left)  → Point 8 (Bottom-Center) → Point 9 (Bottom-Right)
```

**For EACH circle:**

1. **Look at the RED circle** 👀
2. **Press SPACE bar** (you'll see "Sample 1/5")
3. **Keep looking at the circle**
4. **Press SPACE again** (you'll see "Sample 2/5")
5. **Repeat** until you see "Sample 5/5"
6. The circle will **move to the next position**
7. **Repeat** for all 9 circles

### Step 3: Save Calibration

After completing all 9 points:
- You'll see: **"CALIBRATION COMPLETE!"**
- **Press 's'** to save
- You'll see: **"✅ Calibration saved to: calibration/calibration_data.json"**

### Step 4: Close Window
- **Press 'q'** to quit the calibration window

---

## 💡 TIPS

### Do:
- ✅ Keep your head still while looking at each circle
- ✅ Look directly at the center of the RED circle
- ✅ Press SPACE 5 times per circle
- ✅ Take your time - accuracy is important

### Don't:
- ❌ Move your head while pressing SPACE
- ❌ Rush through the points
- ❌ Look away from the circle while capturing
- ❌ Skip any points

---

## 🐛 TROUBLESHOOTING

### "No face detected"
**Problem:** Camera can't see your face
**Solution:**
- Move closer to camera
- Improve lighting
- Remove obstructions (hair, glasses)

### "Multiple faces detected"
**Problem:** More than one person in frame
**Solution:**
- Ensure only you are in frame
- Remove photos/posters from background

### Circle not moving
**Problem:** Not enough samples captured
**Solution:**
- Press SPACE 5 times while looking at the circle
- Make sure your face is visible

### Window not appearing
**Problem:** Calibration window hidden
**Solution:**
- Check your taskbar/dock
- Look for a Python window
- Press Alt+Tab (Windows) or Cmd+Tab (Mac)

---

## 📊 WHAT HAPPENS DURING CALIBRATION

### For Each Point:
```
1. RED circle appears at position
2. You look at the circle
3. Press SPACE → System captures:
   - Your iris position
   - Your gaze vector
   - Your head pose
4. Repeat 5 times for accuracy
5. Circle moves to next position
```

### After All Points:
```
System calculates:
- Screen boundary matrix
- Gaze ranges (left/right/up/down)
- Head pose ranges
- Calibration complete!
```

---

## ✅ AFTER CALIBRATION

### What You'll Have:
- **Screen boundary matrix** created
- **Calibration file** saved: `calibration/calibration_data.json`
- **System ready** for accurate detection

### Next Steps:
1. Close calibration window (press 'q')
2. Go back to interview system at http://localhost:8502
3. You'll see: **"✅ System Calibrated"**
4. Start interview!

---

## 🎯 CURRENT STATUS

**Calibration window:** ✅ OPEN (look for it on your screen)

**What to do now:**
1. Find the calibration window
2. Look at the RED circle
3. Press SPACE 5 times
4. Repeat for all 9 circles
5. Press 's' to save
6. Press 'q' to quit

**Time needed:** 2-3 minutes

---

## 🚀 QUICK REFERENCE

**Look at circle** → **Press SPACE** (5 times) → **Next circle** → **Repeat** → **Press 's'** → **Press 'q'**

**That's it! The calibration window is waiting for you!**
