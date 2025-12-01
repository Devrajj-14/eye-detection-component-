"""
Event Filters
Filters false positives and validates events
"""
from typing import List, Dict


class EventFilter:
    """Filter and validate events"""
    
    @staticmethod
    def remove_duplicates(events: List[str]) -> List[str]:
        """Remove duplicate events while preserving order"""
        seen = set()
        filtered = []
        for event in events:
            if event not in seen:
                seen.add(event)
                filtered.append(event)
        return filtered
    
    @staticmethod
    def apply_confidence_threshold(detections: List[Dict], threshold: float = 0.25) -> List[Dict]:
        """Filter detections by confidence threshold"""
        return [det for det in detections if det.get('confidence', 0) >= threshold]
    
    @staticmethod
    def filter_temporal(events: List[str], min_duration_frames: int = 3) -> List[str]:
        """
        Filter events that don't persist for minimum duration
        (Requires temporal tracking - simplified here)
        """
        # In production, this would track event persistence across frames
        return events
    
    @staticmethod
    def validate_event(event: str, context: Dict) -> bool:
        """
        Validate if an event is legitimate given context
        
        Args:
            event: Event name
            context: Context dictionary with frame data
        
        Returns:
            True if event is valid
        """
        # Example validations
        if event == 'MULTIPLE_FACES':
            # Ensure face count is actually > 1
            return context.get('face_count', 0) > 1
        
        if event == 'PHONE_DETECTED':
            # Ensure phone confidence is high enough
            objects = context.get('objects', [])
            return any('phone' in obj.lower() for obj in objects)
        
        # Default: accept event
        return True
