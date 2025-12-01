# Interview Anti-Cheating Monitor Guide

## 🎓 Overview

The Interview Anti-Cheating Monitoring System is designed to detect and log suspicious behavior during online interviews and exams.

## 🚀 Quick Start

```bash
cd openface_interviewer
source venv/bin/activate
streamlit run interview_monitor.py
```

Access at: **http://localhost:8501**

## 📋 Setup Process

### 1. Enter Interview Details
- **Candidate Name**: Full name of the interviewee
- **Interview ID**: Unique identifier (auto-generated or custom)

### 2. Start Interview
- Click **"Start Interview"** button
- Camera will activate automatically
- Monitoring begins immediately

### 3. Monitor in Real-Time
- Watch live video feed
- View violation alerts
- Check statistics

### 4. End Interview
- Click **"End Interview"** button
- Violations log saved automatically
- Review report in `violations/` folder

## 🚨 Detected Violations

### 1. NO_FACE
**Trigger:** Face not visible for extended period

**Threshold:** 30 frames (adjustable)

**Reasons:**
- Candidate left the room
- Camera covered
- Poor lighting
- Looking down at phone/notes

**Action:** Screenshot captured, violation logged

### 2. MULTIPLE_FACES
**Trigger:** More than one person detected

**Threshold:** Immediate

**Reasons:**
- Someone else in the room
- Another person helping
- Reflection in mirror/screen

**Action:** Screenshot captured, violation logged immediately

### 3. LOOKING_AWAY
**Trigger:** Gaze direction away from screen

**Threshold:** 60 frames (adjustable)

**Detected Directions:**
- Looking left
- Looking right
- Looking down

**Reasons:**
- Reading notes
- Looking at phone
- Checking other screen
- Talking to someone

**Action:** Screenshot captured, violation logged

### 4. SUSPICIOUS_OBJECT
**Trigger:** Prohibited objects detected

**Threshold:** Immediate

**Detected Objects:**
- Cell phone
- Book
- Laptop (additional)
- Keyboard (additional)
- Mouse (additional)
- TV/Monitor (additional)

**Action:** Screenshot captured, violation logged immediately

## ⚙️ Configuration

### Adjustable Thresholds

**No Face Alert (frames):**
- Range: 10-100 frames
- Default: 30 frames
- ~1 second at 30 FPS

**Looking Away Alert (frames):**
- Range: 30-120 frames
- Default: 60 frames
- ~2 seconds at 30 FPS

**Violation Cooldown:**
- Default: 3 seconds
- Prevents spam alerts

## 📊 Monitoring Dashboard

### Live Video Feed
- Real-time face detection
- Gaze direction arrows
- Person ID labels
- Violation status overlay

### Statistics Panel
- Total violations count
- Breakdown by type:
  - No Face incidents
  - Multiple People detections
  - Looking Away instances
  - Objects Detected

### Recent Violations List
- Last 10 violations displayed
- Timestamp for each
- Description of violation
- Screenshot reference

## 📁 Output Files

### Violations Log
**Location:** `violations/interview_[INTERVIEW_ID].json`

**Contents:**
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
    }
  ],
  "total_violations": 5
}
```

### Screenshots
**Location:** `violations/violation_[TIMESTAMP].jpg`

**Captured When:**
- Any violation detected
- Includes timestamp
- Shows violation context

## 🎯 Use Cases

### 1. Online Interviews
- Monitor candidate behavior
- Ensure fair assessment
- Detect unauthorized assistance
- Verify identity

### 2. Online Exams
- Prevent cheating
- Monitor test-takers
- Ensure exam integrity
- Generate compliance reports

### 3. Remote Proctoring
- Real-time monitoring
- Automated violation detection
- Evidence collection
- Post-exam review

## 🔒 Privacy & Compliance

### Data Collection
- Video processed locally
- No cloud transmission
- Screenshots saved locally
- Logs stored on device

### Candidate Notification
- Inform candidates of monitoring
- Explain violation types
- Provide clear guidelines
- Obtain consent

### Data Retention
- Set retention policies
- Secure storage
- Access controls
- GDPR compliance

## 💡 Best Practices

### Before Interview

1. **Test Setup**
   - Run test interview
   - Check camera angle
   - Verify lighting
   - Test detection accuracy

2. **Candidate Instructions**
   - Explain monitoring system
   - List prohibited items
   - Show acceptable behavior
   - Answer questions

3. **Environment Setup**
   - Clear background
   - Good lighting
   - Stable camera
   - Quiet room

### During Interview

1. **Monitor Actively**
   - Watch live feed
   - Check violation alerts
   - Note suspicious patterns
   - Document concerns

2. **Handle Violations**
   - Review context
   - Verify false positives
   - Communicate with candidate
   - Document decisions

3. **Technical Issues**
   - Camera problems
   - Lighting changes
   - Network issues
   - System errors

### After Interview

1. **Review Violations**
   - Check all logged violations
   - Review screenshots
   - Assess severity
   - Make decisions

2. **Generate Report**
   - Compile violation log
   - Include screenshots
   - Add notes/context
   - Share with stakeholders

3. **Data Management**
   - Archive recordings
   - Secure storage
   - Follow retention policy
   - Delete when appropriate

## 🐛 Troubleshooting

### False Positives

**Multiple Faces Detected:**
- Check for reflections
- Remove mirrors
- Adjust camera angle
- Verify background

**Looking Away Alerts:**
- Adjust threshold
- Consider natural eye movement
- Check gaze calibration
- Verify lighting

**Object Detection:**
- Remove similar objects
- Adjust confidence threshold
- Check camera view
- Verify object list

### Performance Issues

**Low FPS:**
- Reduce camera resolution
- Close other applications
- Check system resources
- Improve lighting

**Missed Detections:**
- Improve lighting
- Adjust camera angle
- Check face visibility
- Verify model loading

## 📈 Advanced Features

### Custom Object Detection
Edit `interview_monitor.py`:
```python
suspicious_objects = [
    'cell phone',
    'book',
    'laptop',
    'keyboard',
    'mouse',
    'tv',
    'monitor',
    'tablet',  # Add custom objects
    'notebook'
]
```

### Threshold Adjustment
```python
st.session_state.no_face_threshold = 30
st.session_state.looking_away_threshold = 60
st.session_state.violation_cooldown = 3
```

### Custom Violation Types
Add new violation checks in `check_cheating()` method.

## 📊 Reporting

### Violation Summary
- Total violations
- Breakdown by type
- Timeline of events
- Severity assessment

### Evidence Package
- Violation log (JSON)
- Screenshots
- Timestamp data
- Candidate information

### Compliance Report
- Interview details
- Monitoring duration
- Violation summary
- Recommendations

## 🎓 Training & Support

### For Administrators
- System setup
- Configuration
- Monitoring best practices
- Report generation

### For Proctors
- Live monitoring
- Violation handling
- Communication protocols
- Technical troubleshooting

### For Candidates
- System overview
- Acceptable behavior
- Prohibited items
- Technical requirements

## 🔐 Security Considerations

### Access Control
- Restrict system access
- Secure violation logs
- Protect screenshots
- Audit access logs

### Data Protection
- Encrypt sensitive data
- Secure storage
- Access logging
- Regular backups

### Compliance
- GDPR requirements
- Data retention policies
- Consent management
- Privacy regulations

## 📞 Support

### Documentation
- [README.md](README.md) - Main documentation
- [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md) - Web interface guide
- [USAGE.md](USAGE.md) - Detailed usage

### Common Issues
- Camera not working: Check permissions
- False positives: Adjust thresholds
- Performance: Reduce resolution
- Violations not logging: Check file permissions

## 🎉 Quick Commands

```bash
# Start interview monitor
streamlit run interview_monitor.py

# View violations log
cat violations/interview_[ID].json

# List all violations
ls -la violations/

# Clear old violations
rm -rf violations/*
```

---

**System Status**: ✅ Ready
**Purpose**: Anti-Cheating Monitoring
**Privacy**: Local Processing Only
**Compliance**: Configurable
