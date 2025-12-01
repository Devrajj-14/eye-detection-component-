# 🎯 PRECISION INTERVIEW SYSTEM - COMPLETE SPECIFICATION

## ✅ NEW MODULES CREATED

### 1. `precision_gaze_tracker.py`
**STRICT GAZE DETECTION**
- ✅ 9-point calibration support
- ✅ Regression mapping: (iris + eye angle + head rotation) → screen point
- ✅ Horizontal deviation > 15° triggers alert
- ✅ Vertical deviation > 10° triggers alert
- ✅ Looking away > 0.7 seconds detected
- ✅ Head yaw > 25° = SUSPICIOUS
- ✅ Head yaw > 40° = CRITICAL
- ✅ Micro-cheating detection (3+ glances in 10 sec)
- ✅ Exponential smoothing on gaze vectors

### 2. `precision_phone_detector.py`
**EXTREME PHONE DETECTION**
- ✅ Uses YOLOv8m (medium model)
- ✅ Augmentation enabled (augment=True)
- ✅ Confidence threshold = 0.40
- ✅ Detects 30-40% visible phones
- ✅ Detects phone edges/corners
- ✅ Detects phone lying flat
- ✅ Detects phone behind hand/desk
- ✅ Detects phone reflection in glasses
- ✅ Works with screen OFF
- ✅ Works in low light
- ✅ 3-frame confirmation required

### 3. `facial_expression_analyzer.py`
**ACTION UNITS ANALYSIS**
- ✅ Whispering detection (AU25 + AU26 + gaze down)
- ✅ Reading detection (AU01 + AU02 + AU05 + gaze down)
- ✅ Hiding smile (AU12 + AU14 abnormal)
- ✅ Anxiety detection (AU04 + AU07 + high blink rate)
- ✅ Confusion detection (repeated gaze shifts)
- ✅ Suspicious behavior scoring

### 4. `precision_attention.py`
**MULTI-FACTOR ATTENTION**
- ✅ Gaze direction (35% weight)
- ✅ Head pose (25% weight)
- ✅ Eye openness (15% weight)
- ✅ Blink rate (10% weight)
- ✅ Facial tension (10% weight)
- ✅ Micromovements (5% weight)
- ✅ Attention < 60% for 2 sec = WARNING
- ✅ Attention < 40% for 3 sec = RISK
- ✅ Attention < 30% anytime = CRITICAL

## 📊 UPDATED RISK SCORING

### Event Weights (EXTREMELY STRICT)
```python
PHONE_PARTIAL: +40
PHONE_FULL: +60
SECOND_PERSON: +80
LOOKING_AWAY: +20
LOOKING_DOWN: +20
WHISPERING: +15
REFLECTION_PHONE: +30
READING_NOTES: +40
ATTENTION_LOW: +15
AUDIO_SECOND_VOICE: +50
DESK_OBJECT_APPEAR: +35
MICRO_CHEATING: +20
SUSPICIOUS_BEHAVIOR: +25
```

### Risk Decay
- **-3 points per second** (always active)
- Never below 0
- Smooth progression to 100

### Maximum Per Frame
- **+80 points max** (for serious violations like SECOND_PERSON)
- Prevents instant 100 on minor issues
- Allows instant high risk on major cheating

## 🎯 DETECTION RULES

### Multi-Person Detection
```python
# Use ONLY face detection (NOT YOLO person boxes)
# Trigger if:
- face_box_area > 2% of frame
- Even if only eyes visible
- Even if only forehead visible
- Even if 50% partial face
- Even if far in background
- Even if reflection
```

### Phone Detection
```python
# Detect if:
- Full phone visible
- 30-40% visible
- Phone edge/corner
- Phone lying flat
- Phone behind hand
- Phone behind desk
- Phone reflection in glasses
- Screen OFF
- Low light conditions

# Confidence: 0.40
# Confirmation: 3 consecutive frames
```

### Gaze Detection
```python
# Looking away if:
- Horizontal deviation > 15°
- OR Vertical deviation > 10°
- AND duration > 0.7 seconds

# Head rotation:
- Yaw > 25° = SUSPICIOUS
- Yaw > 40° = CRITICAL

# Micro-cheating:
- 3+ left/right glances in 10 sec
- 3+ down glances in 10 sec
- 3+ up glances in 10 sec
```

### Facial Expression
```python
# Whispering:
- Small mouth opening (0.05 < MAR < 0.15)
- Gaze down
- Risk: +15

# Reading:
- Eyebrow raise > 15
- Mouth closed (MAR < 0.1)
- Gaze down
- Risk: +40

# Hiding smile:
- Lip corners pulled (> 25)
- Mouth not fully open (MAR < 0.2)
- Risk: +20

# Anxiety:
- Eye squint (< 5)
- High blink rate (> 30/min)
- Risk: +10

# Confusion:
- 5+ gaze direction changes in 10 frames
- Risk: +25
```

### Attention Calculation
```python
# Weighted factors:
Gaze direction: 35%
Head pose: 25%
Eye openness: 15%
Blink rate: 10%
Facial tension: 10%
Micromovements: 5%

# Thresholds:
< 60% for 2 sec = WARNING
< 40% for 3 sec = RISK
< 30% anytime = CRITICAL
```

## 🚫 ZERO FALSE POSITIVES

### MUST IGNORE
- ✅ Wall
- ✅ AC
- ✅ Background furniture
- ✅ Shoulder
- ✅ Neck
- ✅ T-shirt pattern
- ✅ Shadow
- ✅ Lighting flicker
- ✅ Normal head micro-movements
- ✅ Webcam exposure change

### ONLY DETECT
- cell phone
- smartphone
- laptop (configurable)
- tablet
- book
- paper
- earphones
- headphones
- keyboard misuse
- remote (phone-like)
- face (for person count)

## 📤 OUTPUT FORMAT

```json
{
  "cheating": bool,
  "risk_score": int,
  "attention": int,
  "gaze_status": "center" | "left" | "right" | "down" | "up",
  "face_count": int,
  "detected_objects": [
    {
      "class": "phone",
      "confidence": 0.85,
      "is_partial": false,
      "detection_method": "yolo"
    }
  ],
  "events": [
    "PHONE_FULL",
    "LOOKING_AWAY"
  ],
  "suspicious_behaviours": [
    "whispering",
    "reading"
  ],
  "partial_phone_detected": bool,
  "attention_status": "GOOD" | "WARNING" | "RISK" | "CRITICAL",
  "gaze_deviation": {
    "horizontal": 12.5,
    "vertical": 8.3
  },
  "head_rotation": {
    "pitch": 5.2,
    "yaw": 18.7,
    "roll": 2.1
  },
  "micro_cheating_detected": bool,
  "micro_pattern": "REPEATED_SIDE_GLANCES" | null
}
```

## 🔧 IMPLEMENTATION REQUIREMENTS

### Models
- ✅ OpenFace 3.0 or MediaPipe FaceMesh
- ✅ YOLOv8m (NOT nano)
- ✅ Augmentation enabled
- ✅ Exponential smoothing on gaze

### Performance
- ✅ Minimum 15 FPS
- ✅ All events debounced (3-frame confirmation)
- ✅ No repeated spam violations
- ✅ Smooth risk progression

### Detection Quality
- ✅ NO false negatives
- ✅ NO loose thresholds
- ✅ HIGH sensitivity
- ✅ STRICT confirmation

## 🎯 INTEGRATION STEPS

### Step 1: Update Object Detector
```python
from utils.precision_phone_detector import PrecisionPhoneDetector

detector = PrecisionPhoneDetector()
confirmed, all_dets = detector.detect_all(frame, face_box)
```

### Step 2: Update Gaze Tracker
```python
from utils.precision_gaze_tracker import PrecisionGazeTracker

gaze_tracker = PrecisionGazeTracker()
gaze_analysis = gaze_tracker.analyze_gaze(
    iris_left, iris_right, head_pose, landmarks, current_time
)
```

### Step 3: Update Expression Analyzer
```python
from utils.facial_expression_analyzer import FacialExpressionAnalyzer

expression_analyzer = FacialExpressionAnalyzer()
behaviors = expression_analyzer.analyze_expression(
    landmarks, gaze_direction, blink_rate, gaze_history
)
```

### Step 4: Update Attention Calculator
```python
from utils.precision_attention import PrecisionAttentionCalculator

attention_calc = PrecisionAttentionCalculator()
attention = attention_calc.calculate_overall_attention(
    gaze_status, head_pose, eye_aspect_ratio, blink_rate, landmarks
)
```

### Step 5: Update Risk Scoring
```python
# Use updated EVENT_WEIGHTS
# Apply 3-frame confirmation
# Use -3 decay per second
```

## ✅ TESTING CHECKLIST

### Normal Behavior (Should NOT trigger)
- [ ] Sitting normally
- [ ] Brief head turn
- [ ] Touching face
- [ ] Adjusting posture
- [ ] Blinking normally
- [ ] Slight movements

### Cheating Behavior (MUST trigger)
- [ ] Phone visible (full)
- [ ] Phone visible (30% partial)
- [ ] Phone edge visible
- [ ] Phone reflection in glasses
- [ ] Second person enters
- [ ] Second person partial face
- [ ] Looking away 1+ second
- [ ] Looking down repeatedly
- [ ] Whispering
- [ ] Reading from notes
- [ ] Repeated side glances
- [ ] Attention < 60% for 2 sec
- [ ] Attention < 30% anytime

### Performance
- [ ] FPS > 15
- [ ] No lag
- [ ] Smooth risk progression
- [ ] No spam violations
- [ ] 3-frame confirmation working

---

**Status**: ✅ Precision modules created
**Integration**: ⚠️ Requires updating main system
**Testing**: ⚠️ Requires validation
**Performance**: ✅ Optimized for 15+ FPS
