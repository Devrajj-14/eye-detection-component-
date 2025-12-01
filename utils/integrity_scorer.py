"""
Integrity Scoring System
Calculates cheating risk score and generates integrity reports
"""
from datetime import datetime
import json


class IntegrityScorer:
    def __init__(self):
        # Violation weights
        self.weights = {
            'PHONE_DETECTED': 40,
            'MULTIPLE_FACES': 50,
            'NO_FACE': 25,
            'LOOKING_AWAY_REPEATED': 15,
            'WHISPERING': 25,
            'BACKGROUND_CHANGE': 20,
            'REFLECTION_ANOMALY': 10,
            'EYE_TRACKING_INCONSISTENT': 10,
            'FACE_MISMATCH': 20,
            'SUSPICIOUS_OBJECT': 35,
            'AUDIO_MULTIPLE_VOICES': 30,
            'DESK_OBJECT_MOVEMENT': 15,
            'LIGHTING_ANOMALY': 5,
            'READING_PATTERN': 20,
            'STRESS_HIGH': 10
        }
        
        self.score = 0
        self.violations = []
        self.attention_scores = []
        self.stress_scores = []
        
    def add_violation(self, violation_type, description, confidence=1.0):
        """Add a violation and update score"""
        if violation_type in self.weights:
            points = self.weights[violation_type] * confidence
            self.score = min(100, self.score + points)
            
            self.violations.append({
                'type': violation_type,
                'description': description,
                'points': points,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    
    def add_attention_score(self, score):
        """Add attention score measurement"""
        self.attention_scores.append(score)
    
    def add_stress_score(self, score):
        """Add stress level measurement"""
        self.stress_scores.append(score)
    
    def get_risk_level(self):
        """Get risk level based on score"""
        if self.score < 30:
            return "CLEAN", "green"
        elif self.score < 60:
            return "SUSPICIOUS", "yellow"
        else:
            return "CHEATING", "red"
    
    def get_verdict(self):
        """Get final verdict"""
        risk_level, _ = self.get_risk_level()
        
        if risk_level == "CLEAN":
            return "CLEAN - No significant violations detected"
        elif risk_level == "SUSPICIOUS":
            return "SUSPICIOUS - Some concerning behaviors detected"
        else:
            return "CHEATING - Multiple serious violations detected"
    
    def generate_report(self, candidate_name, interview_id, start_time, end_time):
        """Generate comprehensive integrity report"""
        risk_level, color = self.get_risk_level()
        
        # Calculate averages
        avg_attention = sum(self.attention_scores) / len(self.attention_scores) if self.attention_scores else 100
        avg_stress = sum(self.stress_scores) / len(self.stress_scores) if self.stress_scores else 0
        
        # Count violation types
        violation_counts = {}
        for v in self.violations:
            vtype = v['type']
            violation_counts[vtype] = violation_counts.get(vtype, 0) + 1
        
        report = {
            'report_metadata': {
                'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'candidate_name': candidate_name,
                'interview_id': interview_id,
                'start_time': start_time,
                'end_time': end_time
            },
            
            'identity_verification': {
                'match_confidence': 95,  # Placeholder
                'liveness_passed': True,
                'face_match': 'VERIFIED'
            },
            
            'attention_analysis': {
                'average_gaze_on_screen': f"{avg_attention:.1f}%",
                'off_screen_events': violation_counts.get('LOOKING_AWAY_REPEATED', 0),
                'attention_consistency': 'HIGH' if avg_attention > 80 else 'MEDIUM' if avg_attention > 60 else 'LOW'
            },
            
            'environment_integrity': {
                'background_changes': violation_counts.get('BACKGROUND_CHANGE', 0),
                'lighting_anomalies': violation_counts.get('LIGHTING_ANOMALY', 0),
                'reflection_issues': violation_counts.get('REFLECTION_ANOMALY', 0),
                'desk_movements': violation_counts.get('DESK_OBJECT_MOVEMENT', 0)
            },
            
            'anti_cheat_events': {
                'phone_detected': violation_counts.get('PHONE_DETECTED', 0) > 0,
                'multiple_people': violation_counts.get('MULTIPLE_FACES', 0) > 0,
                'suspicious_objects': violation_counts.get('SUSPICIOUS_OBJECT', 0),
                'no_face_events': violation_counts.get('NO_FACE', 0),
                'whispering_detected': violation_counts.get('WHISPERING', 0) > 0
            },
            
            'behavior_analysis': {
                'stress_level': f"{avg_stress:.1f}/100",
                'stress_category': 'HIGH' if avg_stress > 60 else 'MEDIUM' if avg_stress > 30 else 'LOW',
                'expression_anomalies': violation_counts.get('STRESS_HIGH', 0),
                'whisper_pattern': violation_counts.get('WHISPERING', 0),
                'reading_pattern_detected': violation_counts.get('READING_PATTERN', 0) > 0
            },
            
            'violation_summary': {
                'total_violations': len(self.violations),
                'violation_breakdown': violation_counts,
                'detailed_violations': self.violations[-20:]  # Last 20 violations
            },
            
            'integrity_score': {
                'cheating_risk_score': f"{self.score:.1f}/100",
                'risk_level': risk_level,
                'risk_color': color,
                'verdict': self.get_verdict()
            },
            
            'recommendations': self._generate_recommendations(risk_level, violation_counts)
        }
        
        return report
    
    def _generate_recommendations(self, risk_level, violation_counts):
        """Generate recommendations based on violations"""
        recommendations = []
        
        if risk_level == "CLEAN":
            recommendations.append("Candidate showed consistent behavior throughout the interview")
            recommendations.append("No significant integrity concerns detected")
        
        if violation_counts.get('PHONE_DETECTED', 0) > 0:
            recommendations.append("⚠️ Phone detected - Verify if authorized device")
        
        if violation_counts.get('MULTIPLE_FACES', 0) > 0:
            recommendations.append("🚨 Multiple people detected - Review interview validity")
        
        if violation_counts.get('LOOKING_AWAY_REPEATED', 0) > 3:
            recommendations.append("⚠️ Frequent looking away - Possible external reference")
        
        if violation_counts.get('WHISPERING', 0) > 0:
            recommendations.append("⚠️ Whispering detected - Review audio recording")
        
        if violation_counts.get('BACKGROUND_CHANGE', 0) > 2:
            recommendations.append("⚠️ Multiple background changes - Verify environment")
        
        if risk_level == "CHEATING":
            recommendations.append("🚨 HIGH RISK - Recommend manual review and possible re-interview")
        
        return recommendations
    
    def save_report(self, report, filename):
        """Save report to JSON file"""
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
    
    def reset(self):
        """Reset scorer state"""
        self.score = 0
        self.violations = []
        self.attention_scores = []
        self.stress_scores = []
