"""
Event Processor
Processes and categorizes detected events
"""
from typing import List, Dict
from enum import Enum


class EventSeverity(Enum):
    """Event severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class EventProcessor:
    """Process and categorize events"""
    
    # Event severity mapping
    EVENT_SEVERITY = {
        'PHONE_DETECTED': EventSeverity.CRITICAL,
        'PHONE_PARTIAL_DETECTED': EventSeverity.HIGH,
        'MULTIPLE_FACES': EventSeverity.CRITICAL,
        'EYES_OFF_SCREEN': EventSeverity.HIGH,
        'LOOKING_AWAY': EventSeverity.MEDIUM,
        'NO_FACE': EventSeverity.HIGH,
        'SUSPICIOUS_OBJECT': EventSeverity.MEDIUM,
        'WHISPERING': EventSeverity.MEDIUM,
        'READING_PATTERN': EventSeverity.MEDIUM,
        'STRESS_HIGH': EventSeverity.LOW,
        'TABLET_DETECTED': EventSeverity.CRITICAL,
    }
    
    @staticmethod
    def get_severity(event: str) -> EventSeverity:
        """Get severity of an event"""
        return EventProcessor.EVENT_SEVERITY.get(event, EventSeverity.LOW)
    
    @staticmethod
    def filter_by_severity(events: List[str], min_severity: EventSeverity) -> List[str]:
        """Filter events by minimum severity"""
        return [
            event for event in events
            if EventProcessor.get_severity(event).value >= min_severity.value
        ]
    
    @staticmethod
    def get_critical_events(events: List[str]) -> List[str]:
        """Get only critical events"""
        return EventProcessor.filter_by_severity(events, EventSeverity.CRITICAL)
    
    @staticmethod
    def categorize_events(events: List[str]) -> Dict[str, List[str]]:
        """Categorize events by type"""
        categories = {
            'gaze': [],
            'objects': [],
            'people': [],
            'behavior': []
        }
        
        for event in events:
            if 'LOOKING' in event or 'EYES' in event or 'GAZE' in event:
                categories['gaze'].append(event)
            elif 'PHONE' in event or 'TABLET' in event or 'OBJECT' in event:
                categories['objects'].append(event)
            elif 'FACE' in event or 'PEOPLE' in event:
                categories['people'].append(event)
            else:
                categories['behavior'].append(event)
        
        return categories
