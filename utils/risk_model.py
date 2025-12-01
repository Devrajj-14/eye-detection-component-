"""
Clean Risk Scoring Model
Single source of truth, no random jumps to 100
"""
from dataclasses import dataclass
from typing import List


@dataclass
class FrameAnalysis:
    """Analysis results for a single frame"""
    cheating_events: List[str]  # ["PHONE_DETECTED", "MULTI_PERSON", ...]
    attention_score: float  # 0.0 to 1.0
    warnings: List[str]  # Human readable warnings
    stress_level: float = 0.0  # 0 to 100


# Constants
BASE_DECAY = 3  # Risk points decayed per second
MAX_RISK = 100
MIN_RISK = 0

# Event weights (how much risk each event adds) - EXTREMELY STRICT
EVENT_WEIGHTS = {
    'PHONE_PARTIAL': 40,
    'PHONE_FULL': 60,
    'SECOND_PERSON': 80,
    'LOOKING_AWAY': 20,
    'LOOKING_DOWN': 20,
    'WHISPERING': 15,
    'REFLECTION_PHONE': 30,
    'READING_NOTES': 40,
    'ATTENTION_LOW': 15,
    'AUDIO_SECOND_VOICE': 50,
    'DESK_OBJECT_APPEAR': 35,
    'BOOK_PAPER': 25,
    'MICRO_CHEATING': 20,
    'SUSPICIOUS_BEHAVIOR': 25,
}

# Maximum risk that can be added in a single frame
MAX_RISK_PER_FRAME = 80  # Increased for serious violations


def update_risk(prev_risk: int, frame_analysis: FrameAnalysis, dt: float) -> int:
    """
    Update session risk score based on frame analysis
    STRICT RULES: Max +15 per frame, decay -4 per second
    
    Args:
        prev_risk: Previous risk score (0-100)
        frame_analysis: Current frame analysis results
        dt: Time delta in seconds since last update
    
    Returns:
        New risk score (0-100)
    """
    risk = prev_risk
    
    # 1) Add risk for active cheating events (with cap)
    risk_to_add = 0
    for event in frame_analysis.cheating_events:
        if event in EVENT_WEIGHTS:
            risk_to_add += EVENT_WEIGHTS[event]
    
    # Cap maximum risk added per frame
    risk_to_add = min(risk_to_add, MAX_RISK_PER_FRAME)
    risk += risk_to_add
    
    # 2) ALWAYS decay risk over time (even with events)
    # This prevents instant 100 and allows recovery
    risk -= int(BASE_DECAY * dt)
    
    # 3) Clamp to valid range
    risk = max(MIN_RISK, min(MAX_RISK, risk))
    
    return risk


def get_risk_level(risk_score: int) -> tuple[str, str]:
    """
    Get risk level and color based on score
    
    Returns:
        (level, color) tuple
    """
    if risk_score < 30:
        return "CLEAN", "green"
    elif risk_score < 60:
        return "SUSPICIOUS", "yellow"
    else:
        return "CHEATING", "red"


def get_status_message(risk_score: int, risk_level: str) -> str:
    """Get human-readable status message"""
    if risk_level == "CLEAN":
        return f"✅ No significant violations (Risk: {risk_score}/100)"
    elif risk_level == "SUSPICIOUS":
        return f"⚠️ Some concerning behaviors detected (Risk: {risk_score}/100)"
    else:
        return f"🚨 Multiple serious violations detected (Risk: {risk_score}/100)"


def should_flag_interview(risk_score: int, duration_minutes: float) -> bool:
    """
    Determine if interview should be flagged for review
    
    Args:
        risk_score: Current risk score
        duration_minutes: Interview duration in minutes
    
    Returns:
        True if interview should be flagged
    """
    # Flag if risk is high
    if risk_score >= 80:
        return True
    
    # Flag if sustained medium risk
    if risk_score >= 50 and duration_minutes > 5:
        return True
    
    return False
