"""
Python Client for AI Interview Integrity API
"""
import requests
import base64
import cv2
import time
from typing import Dict, Optional


class InterviewClient:
    """Python client for the interview integrity API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session_id: Optional[str] = None
    
    def health_check(self) -> Dict:
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def start_session(self, candidate_id: str, metadata: Optional[Dict] = None) -> str:
        """
        Start a new interview session
        
        Args:
            candidate_id: Candidate identifier
            metadata: Optional metadata
        
        Returns:
            Session ID
        """
        payload = {
            "candidate_id": candidate_id,
            "metadata": metadata or {}
        }
        
        response = requests.post(f"{self.base_url}/start-session", json=payload)
        response.raise_for_status()
        
        data = response.json()
        self.session_id = data['session_id']
        return self.session_id
    
    def analyze_frame(self, session_id: str, frame: bytes) -> Dict:
        """
        Analyze a single frame
        
        Args:
            session_id: Session ID
            frame: Image bytes (JPEG/PNG)
        
        Returns:
            Analysis results
        """
        # Encode frame to base64
        frame_b64 = base64.b64encode(frame).decode('utf-8')
        
        payload = {
            "session_id": session_id,
            "frame": frame_b64,
            "timestamp": time.time()
        }
        
        response = requests.post(f"{self.base_url}/analyze-frame", json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def analyze_frame_from_array(self, session_id: str, frame_array) -> Dict:
        """
        Analyze frame from numpy array
        
        Args:
            session_id: Session ID
            frame_array: OpenCV image (BGR numpy array)
        
        Returns:
            Analysis results
        """
        # Encode to JPEG
        _, buffer = cv2.imencode('.jpg', frame_array)
        frame_bytes = buffer.tobytes()
        
        return self.analyze_frame(session_id, frame_bytes)
    
    def end_session(self, session_id: str) -> Dict:
        """
        End interview session
        
        Args:
            session_id: Session ID
        
        Returns:
            Final verdict and summary
        """
        payload = {"session_id": session_id}
        
        response = requests.post(f"{self.base_url}/end-session", json=payload)
        response.raise_for_status()
        
        return response.json()


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = InterviewClient("http://localhost:8000")
    
    # Check health
    health = client.health_check()
    print(f"API Status: {health['status']}")
    
    # Start session
    session_id = client.start_session("candidate_12345")
    print(f"Session started: {session_id}")
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    try:
        frame_count = 0
        while frame_count < 100:  # Analyze 100 frames
            ret, frame = cap.read()
            if not ret:
                break
            
            # Analyze frame
            result = client.analyze_frame_from_array(session_id, frame)
            
            print(f"Frame {frame_count}: Risk={result['risk_score']}, "
                  f"Cheating={result['cheating']}, Events={result['events']}")
            
            frame_count += 1
            time.sleep(0.1)  # 10 FPS
    
    finally:
        cap.release()
        
        # End session
        final = client.end_session(session_id)
        print(f"\nFinal Verdict: {final['verdict']}")
        print(f"Final Risk Score: {final['final_risk_score']}")
        print(f"Total Violations: {final['total_violations']}")
