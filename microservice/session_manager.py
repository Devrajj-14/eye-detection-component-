"""
Session Manager
Manages interview sessions with auto-expiry
"""
import time
from typing import Dict, Optional, List
from collections import defaultdict
import threading


class SessionManager:
    """
    Manages interview sessions with in-memory storage
    Can be extended to use Redis for distributed systems
    """
    
    def __init__(self, expire_after_seconds: int = 900):
        self.sessions: Dict[str, Dict] = {}
        self.expire_after = expire_after_seconds
        self.lock = threading.Lock()
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def create_session(self, session_id: str, candidate_id: str, metadata: Dict) -> None:
        """Create a new session"""
        with self.lock:
            self.sessions[session_id] = {
                'session_id': session_id,
                'candidate_id': candidate_id,
                'metadata': metadata,
                'start_time': time.time(),
                'last_activity': time.time(),
                'risk_score': 0,
                'events': [],
                'frame_count': 0,
                'attention_scores': [],
                'average_attention': 100
            }
    
    def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        with self.lock:
            return session_id in self.sessions
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        with self.lock:
            session = self.sessions.get(session_id)
            if session:
                session['last_activity'] = time.time()
            return session
    
    def update_session(self, session_id: str, risk_score: float, events: List[str]) -> None:
        """Update session with new data"""
        with self.lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session['risk_score'] = risk_score
                session['events'].extend(events)
                session['frame_count'] += 1
                session['last_activity'] = time.time()
    
    def close_session(self, session_id: str) -> None:
        """Close and remove session"""
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
    
    def get_active_count(self) -> int:
        """Get number of active sessions"""
        with self.lock:
            return len(self.sessions)
    
    def get_event_breakdown(self, session_id: str) -> Dict[str, int]:
        """Get breakdown of events for a session"""
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return {}
            
            breakdown = defaultdict(int)
            for event in session['events']:
                breakdown[event] += 1
            
            return dict(breakdown)
    
    def cleanup_expired(self) -> int:
        """Remove expired sessions"""
        current_time = time.time()
        expired = []
        
        with self.lock:
            for session_id, session in self.sessions.items():
                if current_time - session['last_activity'] > self.expire_after:
                    expired.append(session_id)
            
            for session_id in expired:
                del self.sessions[session_id]
        
        return len(expired)
    
    def cleanup_all(self) -> None:
        """Remove all sessions"""
        with self.lock:
            self.sessions.clear()
    
    def _start_cleanup_thread(self) -> None:
        """Start background thread for cleanup"""
        def cleanup_loop():
            while True:
                time.sleep(60)  # Check every minute
                count = self.cleanup_expired()
                if count > 0:
                    print(f"🧹 Cleaned up {count} expired sessions")
        
        thread = threading.Thread(target=cleanup_loop, daemon=True)
        thread.start()
