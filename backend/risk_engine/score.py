"""
Risk Scoring Engine
"""
from typing import List


class RiskEngine:
    """Risk scoring with decay"""
    
    RISK_INCREASES = {
        'PHONE_DETECTED': 30,
        'PHONE_PARTIAL': 20,
        'MULTIPLE_FACES': 25,
        'EYES_OFF_SCREEN': 15,
        'LOOKING_AWAY': 10,
        'NO_FACE': 20,
        'SUSPICIOUS_OBJECT': 15,
        'WHISPERING': 10,
        'READING_PATTERN': 12,
        'STRESS_HIGH': 5,
    }
    
    DECAY_RATE = 2.0  # Points per second
    
    def update_risk(
        self,
        current_risk: float,
        events: List[str],
        attention: float,
        dt: float = 0.033
    ) -> float:
        """Update risk score"""
        # Apply decay
        risk = max(0, current_risk - (self.DECAY_RATE * dt))
        
        # Add risk for events
        for event in events:
            if event in self.RISK_INCREASES:
                risk += self.RISK_INCREASES[event]
        
        # Attention penalty
        if attention < 50:
            risk += (50 - attention) * 0.1 * dt
        
        # Clamp to 0-100
        return max(0, min(100, risk))
    
    def get_verdict(self, risk_score: float) -> str:
        """Get final verdict"""
        if risk_score >= 50:
            return "CHEATING"
        elif risk_score >= 30:
            return "SUSPICIOUS"
        else:
            return "CLEAN"
