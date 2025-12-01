"""
Risk Scoring Engine
Calculates and updates risk scores based on detected events
"""
from typing import List, Dict
import time


class RiskEngine:
    """
    Risk scoring engine with decay and event-based updates
    """
    
    # Risk increase per event type
    RISK_INCREASES = {
        'PHONE_DETECTED': 30,
        'PHONE_PARTIAL_DETECTED': 20,
        'MULTIPLE_FACES': 25,
        'EYES_OFF_SCREEN': 15,
        'LOOKING_AWAY': 10,
        'NO_FACE': 20,
        'SUSPICIOUS_OBJECT': 15,
        'WHISPERING': 10,
        'READING_PATTERN': 12,
        'STRESS_HIGH': 5,
    }
    
    # Risk decay rate (per second)
    DECAY_RATE = 2.0  # Risk decreases by 2 points per second
    
    # Risk thresholds
    THRESHOLD_SUSPICIOUS = 30
    THRESHOLD_CHEATING = 50
    
    def __init__(self):
        self.last_update_time = time.time()
    
    def update_risk(
        self,
        current_risk: float,
        events: List[str],
        attention: float,
        dt: float = 0.033
    ) -> float:
        """
        Update risk score based on events and attention
        
        Args:
            current_risk: Current risk score (0-100)
            events: List of detected events
            attention: Attention score (0-100)
            dt: Time delta since last update (seconds)
        
        Returns:
            Updated risk score (0-100)
        """
        # Apply decay
        risk = max(0, current_risk - (self.DECAY_RATE * dt))
        
        # Add risk for events
        for event in events:
            if event in self.RISK_INCREASES:
                risk += self.RISK_INCREASES[event]
        
        # Attention penalty (low attention increases risk slightly)
        if attention < 50:
            risk += (50 - attention) * 0.1 * dt
        
        # Clamp to 0-100
        risk = max(0, min(100, risk))
        
        return risk
    
    def get_risk_level(self, risk_score: float) -> str:
        """
        Get risk level category
        
        Args:
            risk_score: Risk score (0-100)
        
        Returns:
            Risk level: "CLEAN", "SUSPICIOUS", or "CHEATING"
        """
        if risk_score >= self.THRESHOLD_CHEATING:
            return "CHEATING"
        elif risk_score >= self.THRESHOLD_SUSPICIOUS:
            return "SUSPICIOUS"
        else:
            return "CLEAN"
    
    def get_verdict(self, final_risk_score: float) -> str:
        """
        Get final verdict based on risk score
        
        Args:
            final_risk_score: Final risk score (0-100)
        
        Returns:
            Verdict: "CHEATING", "SUSPICIOUS", or "CLEAN"
        """
        return self.get_risk_level(final_risk_score)
    
    def calculate_confidence(self, risk_score: float, event_count: int) -> float:
        """
        Calculate confidence in the risk assessment
        
        Args:
            risk_score: Current risk score
            event_count: Number of events detected
        
        Returns:
            Confidence score (0-1)
        """
        # More events = higher confidence
        event_confidence = min(1.0, event_count / 10)
        
        # Extreme scores = higher confidence
        score_confidence = abs(risk_score - 50) / 50
        
        # Combined confidence
        confidence = (event_confidence + score_confidence) / 2
        
        return confidence
    
    def get_risk_breakdown(self, events: List[str]) -> Dict[str, int]:
        """
        Get breakdown of risk by event type
        
        Args:
            events: List of all events
        
        Returns:
            Dictionary of event types and their risk contributions
        """
        breakdown = {}
        
        for event in events:
            if event in self.RISK_INCREASES:
                breakdown[event] = breakdown.get(event, 0) + self.RISK_INCREASES[event]
        
        return breakdown
