"""Event Filters"""
from typing import List


class EventFilter:
    """Filter and validate events"""
    
    @staticmethod
    def remove_duplicates(events: List[str]) -> List[str]:
        """Remove duplicate events"""
        seen = set()
        filtered = []
        for event in events:
            if event not in seen:
                seen.add(event)
                filtered.append(event)
        return filtered
    
    @staticmethod
    def validate(event: str, context: dict) -> bool:
        """Validate event"""
        if event == 'MULTIPLE_FACES':
            return context.get('face_count', 0) > 1
        if event == 'PHONE_DETECTED':
            return any('phone' in obj.lower() for obj in context.get('objects', []))
        return True
