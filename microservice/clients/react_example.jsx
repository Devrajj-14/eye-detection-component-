/**
 * React Component for AI Interview Integrity Monitoring
 */
import React, { useState, useRef, useEffect } from 'react';

const InterviewMonitor = ({ apiUrl = 'http://localhost:8000', candidateId }) => {
    const [sessionId, setSessionId] = useState(null);
    const [riskScore, setRiskScore] = useState(0);
    const [cheating, setCheating] = useState(false);
    const [events, setEvents] = useState([]);
    const [isMonitoring, setIsMonitoring] = useState(false);
    
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const intervalRef = useRef(null);

    // Start interview session
    const startSession = async () => {
        try {
            const response = await fetch(`${apiUrl}/start-session`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    candidate_id: candidateId,
                    metadata: {}
                })
            });

            const data = await response.json();
            setSessionId(data.session_id);
            
            // Start webcam
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            videoRef.current.srcObject = stream;
            
            setIsMonitoring(true);
            startFrameAnalysis(data.session_id);
        } catch (error) {
            console.error('Error starting session:', error);
        }
    };

    // Analyze frames periodically
    const startFrameAnalysis = (sessionId) => {
        intervalRef.current = setInterval(async () => {
            if (!videoRef.current || !canvasRef.current) return;

            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');
            
            canvas.width = videoRef.current.videoWidth;
            canvas.height = videoRef.current.videoHeight;
            ctx.drawImage(videoRef.current, 0, 0);

            // Convert to base64
            const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
            const frameBase64 = dataUrl.split(',')[1];

            try {
                const response = await fetch(`${apiUrl}/analyze-frame`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        frame: frameBase64,
                        timestamp: Date.now() / 1000
                    })
                });

                const result = await response.json();
                
                setRiskScore(result.risk_score);
                setCheating(result.cheating);
                setEvents(result.events);
            } catch (error) {
                console.error('Error analyzing frame:', error);
            }
        }, 1000); // 1 FPS
    };

    // End session
    const endSession = async () => {
        if (!sessionId) return;

        try {
            const response = await fetch(`${apiUrl}/end-session`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });

            const result = await response.json();
            
            alert(`Interview Ended\nVerdict: ${result.verdict}\nFinal Risk: ${result.final_risk_score}`);
            
            // Stop monitoring
            clearInterval(intervalRef.current);
            setIsMonitoring(false);
            
            // Stop webcam
            if (videoRef.current && videoRef.current.srcObject) {
                videoRef.current.srcObject.getTracks().forEach(track => track.stop());
            }
        } catch (error) {
            console.error('Error ending session:', error);
        }
    };

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
            if (videoRef.current && videoRef.current.srcObject) {
                videoRef.current.srcObject.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1>AI Interview Integrity Monitor</h1>
            
            <div style={{ marginBottom: '20px' }}>
                <video 
                    ref={videoRef} 
                    autoPlay 
                    style={{ width: '640px', height: '480px', border: '2px solid #ccc' }}
                />
                <canvas ref={canvasRef} style={{ display: 'none' }} />
            </div>

            <div style={{ marginBottom: '20px' }}>
                {!isMonitoring ? (
                    <button 
                        onClick={startSession}
                        style={{ padding: '10px 20px', fontSize: '16px', cursor: 'pointer' }}
                    >
                        Start Interview
                    </button>
                ) : (
                    <button 
                        onClick={endSession}
                        style={{ padding: '10px 20px', fontSize: '16px', cursor: 'pointer', backgroundColor: '#f44336', color: 'white' }}
                    >
                        End Interview
                    </button>
                )}
            </div>

            {isMonitoring && (
                <div style={{ 
                    padding: '20px', 
                    backgroundColor: cheating ? '#ffebee' : '#e8f5e9',
                    border: `2px solid ${cheating ? '#f44336' : '#4caf50'}`,
                    borderRadius: '8px'
                }}>
                    <h2>Monitoring Status</h2>
                    <p><strong>Session ID:</strong> {sessionId}</p>
                    <p><strong>Risk Score:</strong> {riskScore}/100</p>
                    <p><strong>Cheating Detected:</strong> {cheating ? '🚨 YES' : '✅ NO'}</p>
                    
                    {events.length > 0 && (
                        <div>
                            <strong>Recent Events:</strong>
                            <ul>
                                {events.map((event, index) => (
                                    <li key={index}>{event}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default InterviewMonitor;

// Usage example:
// <InterviewMonitor apiUrl="http://localhost:8000" candidateId="candidate_123" />
