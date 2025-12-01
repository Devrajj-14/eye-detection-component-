# Interview Monitor - Quick Start

## 🚀 Launch Application

```bash
cd openface_interviewer
source venv/bin/activate
streamlit run interview_monitor.py
```

**Access:** http://localhost:8501

## 📋 Setup (30 seconds)

1. **Enter Details**
   - Candidate Name: `John Doe`
   - Interview ID: Auto-generated or custom

2. **Click "Start Interview"**
   - Camera activates
   - Monitoring begins

3. **Monitor Live**
   - Watch video feed
   - Check violation alerts
   - Review statistics

4. **End Interview**
   - Click "End Interview"
   - Report saved automatically

## 🚨 What Gets Detected

| Violation | Description | Action |
|-----------|-------------|--------|
| **NO_FACE** | Face not visible | Screenshot + Log |
| **MULTIPLE_FACES** | 2+ people detected | Screenshot + Log |
| **LOOKING_AWAY** | Not looking at screen | Screenshot + Log |
| **SUSPICIOUS_OBJECT** | Phone, book, laptop | Screenshot + Log |

## 📊 Dashboard Overview

```
┌─────────────────────────────────────────────────────┐
│  🎓 Interview Anti-Cheating Monitor                 │
├──────────────┬──────────────────────────────────────┤
│              │                                       │
│  Sidebar     │  Live Video Feed                      │
│  ─────────   │  ┌─────────────────────────────┐     │
│  📋 Setup    │  │                             │     │
│  Name: ___   │  │   [Live Camera]             │     │
│  ID: ___     │  │   + Face Detection          │     │
│  🚀 Start    │  │   + Gaze Tracking           │     │
│              │  │   + Object Detection        │     │
│  ⚙️ Settings │  └─────────────────────────────┘     │
│  Thresholds  │                                       │
│              │  ⚠️ Recent Violations                 │
│  📊 Stats    │  • NO_FACE - 23:05:30                │
│  Total: 5    │  • MULTIPLE_FACES - 23:10:15         │
│  No Face: 2  │  • LOOKING_AWAY - 23:12:45           │
│  Multiple: 1 │                                       │
│  Looking: 1  │                                       │
│  Objects: 1  │                                       │
└──────────────┴──────────────────────────────────────┘
```

## ⚙️ Adjust Settings

**No Face Alert:**
- Slider: 10-100 frames
- Default: 30 frames (~1 second)

**Looking Away Alert:**
- Slider: 30-120 frames
- Default: 60 frames (~2 seconds)

## 📁 Output Files

**Violations Log:**
```
violations/interview_INT_20241201_230000.json
```

**Screenshots:**
```
violations/violation_20241201_230530.jpg
violations/violation_20241201_231015.jpg
```

## 🎯 Best Practices

### Before Starting
✅ Test camera and lighting
✅ Explain system to candidate
✅ Clear background
✅ Remove prohibited items

### During Interview
✅ Monitor live feed
✅ Check violation alerts
✅ Note suspicious patterns
✅ Verify false positives

### After Interview
✅ Review violation log
✅ Check screenshots
✅ Generate report
✅ Archive data

## 🚨 Violation Examples

### ❌ NO_FACE
```
Candidate left camera view
Looking down at phone/notes
Camera covered
Poor lighting
```

### ❌ MULTIPLE_FACES
```
Someone else in room
Another person helping
Reflection in mirror
```

### ❌ LOOKING_AWAY
```
Reading notes (left/right)
Checking phone (down)
Looking at another screen
Talking to someone
```

### ❌ SUSPICIOUS_OBJECT
```
Cell phone visible
Book on desk
Additional laptop
Keyboard/mouse (extra)
```

## 💡 Tips

**Reduce False Positives:**
- Adjust thresholds higher
- Improve lighting
- Clear background
- Stable camera position

**Improve Detection:**
- Good lighting
- Clear camera view
- Neutral background
- Proper distance

**Handle Violations:**
- Review context
- Check screenshots
- Communicate with candidate
- Document decisions

## 📊 Sample Report

```json
{
  "interview_id": "INT_20241201_230000",
  "candidate": "John Doe",
  "start_time": "2024-12-01 23:00:00",
  "violations": [
    {
      "timestamp": "2024-12-01 23:05:30",
      "type": "MULTIPLE_FACES",
      "description": "Multiple people detected (2 faces)",
      "screenshot": "violations/violation_20241201_230530.jpg"
    },
    {
      "timestamp": "2024-12-01 23:10:15",
      "type": "SUSPICIOUS_OBJECT",
      "description": "Suspicious object detected: cell phone (confidence: 0.87)",
      "screenshot": "violations/violation_20241201_231015.jpg"
    }
  ],
  "total_violations": 2
}
```

## 🔧 Troubleshooting

**Camera not working:**
```bash
# Check permissions in System Settings
# macOS: Privacy & Security > Camera
```

**Too many false positives:**
```
Increase thresholds in sidebar
Improve lighting
Clear background
```

**Violations not logging:**
```bash
# Check folder permissions
mkdir -p violations
chmod 755 violations
```

## 📞 Quick Help

| Issue | Solution |
|-------|----------|
| No camera | Check permissions |
| False alerts | Increase thresholds |
| Low FPS | Reduce resolution |
| No violations log | Check file permissions |

## 🎉 One-Line Commands

```bash
# Start monitor
streamlit run interview_monitor.py

# View violations
cat violations/interview_*.json

# List screenshots
ls -la violations/*.jpg

# Clear old data
rm -rf violations/*
```

---

**Status**: ✅ Running at http://localhost:8501
**Purpose**: Anti-Cheating Interview Monitoring
**Privacy**: All processing local, no cloud
**Ready**: Start your first interview! 🚀
