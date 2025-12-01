"""Event Processing"""
from typing import List, Dict


class EventProcessor:
    """Process and categorize events"""
    
    @staticmethod
    def categorize(events: List[str]) -> Dict[str, List[str]]:
        """Categorize events by type"""
        categories = {
            'gaze': [],
            'objects': [],
            'people': [],
            'behavior': []
        }
        
        for event in events:
            if 'LOOKING' in event or 'EYES' in event:
                categories['gaze'].append(event)
            elif 'PHONE' in event or 'OBJECT' in event:
                categories['objects'].append(event)
            elif 'FACE' in event:
                categories['people'].append(event)
            else:
                categories['behavior'].append(event)
        
        return categories
