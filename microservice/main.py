"""
AI Interview Integrity Microservice
FastAPI-based stateless API for cheating detection
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import base64
import numpy as np
import cv2
import uuid
import time
from datetime import datetime, timedelta
import asyncio

from risk_engine.score import RiskEngine
from frame_processing.processor import FrameProcessor
from session_manager import SessionManager

# Initialize FastAPI
app = FastAPI(
    title="AI Interview Integrity API",
    description="Real-time cheating detection microservice",
    version="1.0.0"
)

# CORS middleware
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
session_manager: Optional[SessionManager] = None


# ==================== MODELS ====================

class AnalyzeFrameRequest(BaseModel):
    frame: str  # base64 encoded image
    session_id: str
    timestamp: Optional[float] = None


class AnalyzeFrameResponse(BaseModel):
    session_id: str
    cheating: bool
    risk_score: int
    attention: int
    gaze: str
    faces: int
    objects: List[str]
    events: List[str]
    processing_time_ms: float
    timestamp: float


class StartSessionRequest(BaseModel):
    candidate_id: str
    metadata: Optional[Dict] = None


class StartSessionResponse(BaseModel):
    session_id: str
    message: str
    timestamp: float


class EndSessionRequest(BaseModel):
    session_id: str


class EndSessionResponse(BaseModel):
    session_id: str
    final_risk_score: int
    verdict: str  # "CHEATING" | "SUSPICIOUS" | "CLEAN"
    total_violations: int
    duration_seconds: float
    summary: Dict


class HealthResponse(BaseModel):
    status: str
    service: str
    uptime_seconds: float
    active_sessions: int
    models_loaded: bool


# ==================== STARTUP/SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Initialize models and services on startup"""
    global frame_processor, risk_engine, session_manager
    
    print("🚀 Starting AI Interview Integrity Microservice...")
    
    # Initialize frame processor (loads all ML models)
    print("📦 Loading ML models...")
    frame_processor = FrameProcessor()
    await frame_processor.initialize()
    
    # Initialize risk engine
    print("🎯 Initializing risk engine...")
    risk_engine = RiskEngine()
    
    # Initialize session manager
    print("💾 Initializing session manager...")
    session_manager = SessionManager(expire_after_seconds=900)  # 15 min
    
    print("✅ Microservice ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global session_manager
    
    print("🛑 Shutting down microservice...")
    
    if session_manager:
        session_manager.cleanup_all()
    
    print("✅ Shutdown complete")


# ==================== ENDPOINTS ====================

@app.get("/", response_model=Dict)
async def root():
    """Root endpoint"""
    return {
        "service": "AI Interview Integrity API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze-frame",
            "start": "/start-session",
            "end": "/end-session",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    global frame_processor, session_manager
    
    uptime = time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
    
    return HealthResponse(
        status="ok",
        service="ai-interview-monitor",
        uptime_seconds=uptime,
        active_sessions=session_manager.get_active_count() if session_manager else 0,
        models_loaded=frame_processor is not None and frame_processor.is_ready()
    )


@app.post("/start-session", response_model=StartSessionResponse)
async def start_session(request: StartSessionRequest):
    """Start a new interview session"""
    global session_manager
    
    if not session_manager:
        raise HTTPException(status_code=503, detail="Session manager not initialized")
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Create session
    session_manager.create_session(
        session_id=session_id,
        candidate_id=request.candidate_id,
        metadata=request.metadata or {}
    )
    
    return StartSessionResponse(
        session_id=session_id,
        message="Session started successfully",
        timestamp=time.time()
    )


@app.post("/analyze-frame", response_model=AnalyzeFrameResponse)
async def analyze_frame(request: AnalyzeFrameRequest):
    """Analyze a single frame for cheating detection"""
    global frame_processor, risk_engine, session_manager
    
    start_time = time.time()
    
    # Validate services
    if not frame_processor or not risk_engine or not session_manager:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    # Validate session
    if not session_manager.session_exists(request.session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Decode base64 frame
        frame_data = base64.b64decode(request.frame)
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Process frame
        analysis = await frame_processor.process_frame(frame)
        
        # Update risk score
        session_data = session_manager.get_session(request.session_id)
        current_risk = session_data.get('risk_score', 0)
        
        new_risk = risk_engine.update_risk(
            current_risk=current_risk,
            events=analysis['events'],
            attention=analysis['attention'],
            dt=0.033  # ~30fps
        )
        
        # Update session
        session_manager.update_session(
            session_id=request.session_id,
            risk_score=new_risk,
            events=analysis['events']
        )
        
        # Determine if cheating
        cheating = new_risk > 50 or any(
            event in ['PHONE_DETECTED', 'MULTIPLE_FACES', 'EYES_OFF_SCREEN']
            for event in analysis['events']
        )
        
        processing_time = (time.time() - start_time) * 1000  # ms
        
        return AnalyzeFrameResponse(
            session_id=request.session_id,
            cheating=cheating,
            risk_score=int(new_risk),
            attention=int(analysis['attention']),
            gaze=analysis['gaze'],
            faces=analysis['faces'],
            objects=analysis['objects'],
            events=analysis['events'],
            processing_time_ms=round(processing_time, 2),
            timestamp=request.timestamp or time.time()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/end-session", response_model=EndSessionResponse)
async def end_session(request: EndSessionRequest):
    """End an interview session and get final verdict"""
    global session_manager, risk_engine
    
    if not session_manager:
        raise HTTPException(status_code=503, detail="Session manager not initialized")
    
    # Get session data
    session_data = session_manager.get_session(request.session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Calculate final verdict
    final_risk = session_data.get('risk_score', 0)
    verdict = risk_engine.get_verdict(final_risk)
    
    # Get summary
    summary = {
        'candidate_id': session_data.get('candidate_id'),
        'start_time': session_data.get('start_time'),
        'end_time': time.time(),
        'total_events': len(session_data.get('events', [])),
        'event_breakdown': session_manager.get_event_breakdown(request.session_id),
        'average_attention': session_data.get('average_attention', 100)
    }
    
    duration = time.time() - session_data.get('start_time', time.time())
    
    # Close session
    session_manager.close_session(request.session_id)
    
    return EndSessionResponse(
        session_id=request.session_id,
        final_risk_score=int(final_risk),
        verdict=verdict,
        total_violations=len(session_data.get('events', [])),
        duration_seconds=round(duration, 2),
        summary=summary
    )


@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time frame streaming"""
    await websocket.accept()
    
    session_id = None
    
    try:
        while True:
            # Receive data
            data = await websocket.receive_json()
            
            # Handle session start
            if data.get('action') == 'start':
                session_id = str(uuid.uuid4())
                session_manager.create_session(
                    session_id=session_id,
                    candidate_id=data.get('candidate_id', 'unknown'),
                    metadata={}
                )
                await websocket.send_json({
                    'type': 'session_started',
                    'session_id': session_id
                })
                continue
            
            # Handle frame
            if data.get('action') == 'frame' and session_id:
                # Process frame (similar to analyze_frame)
                frame_data = base64.b64decode(data['frame'])
                nparr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                analysis = await frame_processor.process_frame(frame)
                
                # Update risk
                session_data = session_manager.get_session(session_id)
                current_risk = session_data.get('risk_score', 0)
                new_risk = risk_engine.update_risk(
                    current_risk=current_risk,
                    events=analysis['events'],
                    attention=analysis['attention'],
                    dt=0.033
                )
                
                session_manager.update_session(
                    session_id=session_id,
                    risk_score=new_risk,
                    events=analysis['events']
                )
                
                # Send response
                await websocket.send_json({
                    'type': 'analysis',
                    'session_id': session_id,
                    'risk_score': int(new_risk),
                    'attention': int(analysis['attention']),
                    'gaze': analysis['gaze'],
                    'events': analysis['events'],
                    'cheating': new_risk > 50
                })
            
            # Handle session end
            if data.get('action') == 'end' and session_id:
                session_data = session_manager.get_session(session_id)
                final_risk = session_data.get('risk_score', 0)
                verdict = risk_engine.get_verdict(final_risk)
                
                await websocket.send_json({
                    'type': 'session_ended',
                    'session_id': session_id,
                    'final_risk_score': int(final_risk),
                    'verdict': verdict
                })
                
                session_manager.close_session(session_id)
                break
                
    except WebSocketDisconnect:
        if session_id:
            session_manager.close_session(session_id)
    except Exception as e:
        await websocket.send_json({
            'type': 'error',
            'message': str(e)
        })


# Store start time
@app.on_event("startup")
async def store_start_time():
    app.state.start_time = time.time()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
