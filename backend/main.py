"""
AI Interview Integrity Backend Service
FastAPI microservice for cheating detection
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import base64
import numpy as np
import cv2
import uuid
import time
from datetime import datetime

from risk_engine.score import RiskEngine
from frame_processor.processor import FrameProcessor

# Initialize FastAPI
app = FastAPI(
    title="AI Interview Integrity API",
    description="Real-time cheating detection service",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (loaded once at startup)
frame_processor: Optional[FrameProcessor] = None
risk_engine: Optional[RiskEngine] = None

# Session storage (in-memory dictionary)
sessions: Dict[str, Dict] = {}


# ==================== MODELS ====================

class StartSessionRequest(BaseModel):
    candidate_id: str
    metadata: Optional[Dict] = None


class StartSessionResponse(BaseModel):
    session_id: str
    message: str
    timestamp: float


class AnalyzeFrameRequest(BaseModel):
    session_id: str
    frame: str  # base64 encoded


class AnalyzeFrameResponse(BaseModel):
    session_id: str
    cheating: bool
    risk_score: int
    attention: int
    gaze: str
    faces: int
    objects: List[str]
    events: List[str]


class EndSessionRequest(BaseModel):
    session_id: str


class EndSessionResponse(BaseModel):
    session_id: str
    final_risk_score: int
    verdict: str
    total_violations: int
    duration_seconds: float


class HealthResponse(BaseModel):
    status: str
    service: str
    models_loaded: bool
    active_sessions: int


# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global frame_processor, risk_engine
    
    print("🚀 Starting AI Interview Integrity Service...")
    
    # Initialize frame processor
    print("📦 Loading ML models...")
    frame_processor = FrameProcessor()
    frame_processor.initialize()
    
    # Initialize risk engine
    print("🎯 Initializing risk engine...")
    risk_engine = RiskEngine()
    
    print("✅ Service ready!")


# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Interview Integrity API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        service="ai-interview-monitor",
        models_loaded=frame_processor is not None,
        active_sessions=len(sessions)
    )


@app.post("/start-session", response_model=StartSessionResponse)
async def start_session(request: StartSessionRequest):
    """Start a new interview session"""
    # Generate UUID
    session_id = str(uuid.uuid4())
    
    # Initialize session state
    sessions[session_id] = {
        'session_id': session_id,
        'candidate_id': request.candidate_id,
        'metadata': request.metadata or {},
        'start_time': time.time(),
        'risk_score': 0,
        'events': [],
        'frame_count': 0
    }
    
    return StartSessionResponse(
        session_id=session_id,
        message="Session started successfully",
        timestamp=time.time()
    )


@app.post("/analyze-frame", response_model=AnalyzeFrameResponse)
async def analyze_frame(request: AnalyzeFrameRequest):
    """Analyze a single frame for cheating detection"""
    global frame_processor, risk_engine
    
    # Validate session
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not frame_processor or not risk_engine:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    try:
        # Decode base64 frame
        frame_data = base64.b64decode(request.frame)
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Process frame
        analysis = frame_processor.process_frame(frame)
        
        # Update risk score
        session = sessions[request.session_id]
        current_risk = session['risk_score']
        
        new_risk = risk_engine.update_risk(
            current_risk=current_risk,
            events=analysis['events'],
            attention=analysis['attention'],
            dt=0.033  # ~30fps
        )
        
        # Update session
        session['risk_score'] = new_risk
        session['events'].extend(analysis['events'])
        session['frame_count'] += 1
        
        # Determine if cheating
        cheating = new_risk > 50 or any(
            event in ['PHONE_DETECTED', 'MULTIPLE_FACES', 'EYES_OFF_SCREEN']
            for event in analysis['events']
        )
        
        return AnalyzeFrameResponse(
            session_id=request.session_id,
            cheating=cheating,
            risk_score=int(new_risk),
            attention=int(analysis['attention']),
            gaze=analysis['gaze'],
            faces=analysis['faces'],
            objects=analysis['objects'],
            events=analysis['events']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/end-session", response_model=EndSessionResponse)
async def end_session(request: EndSessionRequest):
    """End an interview session and get final verdict"""
    global risk_engine
    
    # Get session
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    
    # Calculate final verdict
    final_risk = session['risk_score']
    verdict = risk_engine.get_verdict(final_risk)
    
    duration = time.time() - session['start_time']
    total_violations = len(session['events'])
    
    # Remove session
    del sessions[request.session_id]
    
    return EndSessionResponse(
        session_id=request.session_id,
        final_risk_score=int(final_risk),
        verdict=verdict,
        total_violations=total_violations,
        duration_seconds=round(duration, 2)
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
