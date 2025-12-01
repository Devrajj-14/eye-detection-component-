/**
 * JavaScript Client for AI Interview Integrity API
 * Works in Node.js and Browser
 */

class InterviewClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.sessionId = null;
    }

    /**
     * Check API health
     */
    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        return await response.json();
    }

    /**
     * Start a new interview session
     */
    async startSession(candidateId, metadata = {}) {
        const response = await fetch(`${this.baseUrl}/start-session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                candidate_id: candidateId,
                metadata: metadata
            })
        });

        const data = await response.json();
        this.sessionId = data.session_id;
        return this.sessionId;
    }

    /**
     * Analyze a single frame
     */
    async analyzeFrame(sessionId, frameBase64) {
        const response = await fetch(`${this.baseUrl}/analyze-frame`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                frame: frameBase64,
                timestamp: Date.now() / 1000
            })
        });

        return await response.json();
    }

    /**
     * Analyze frame from canvas
     */
    async analyzeFrameFromCanvas(sessionId, canvas) {
        // Convert canvas to base64
        const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
        const frameBase64 = dataUrl.split(',')[1];

        return await this.analyzeFrame(sessionId, frameBase64);
    }

    /**
     * End interview session
     */
    async endSession(sessionId) {
        const response = await fetch(`${this.baseUrl}/end-session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });

        return await response.json();
    }

    /**
     * WebSocket streaming (for real-time)
     */
    connectWebSocket(candidateId, onMessage) {
        const ws = new WebSocket(`${this.baseUrl.replace('http', 'ws')}/ws/stream`);

        ws.onopen = () => {
            // Start session
            ws.send(JSON.stringify({
                action: 'start',
                candidate_id: candidateId
            }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            onMessage(data);

            if (data.type === 'session_started') {
                this.sessionId = data.session_id;
            }
        };

        return ws;
    }

    /**
     * Send frame via WebSocket
     */
    sendFrameWS(ws, frameBase64) {
        ws.send(JSON.stringify({
            action: 'frame',
            frame: frameBase64
        }));
    }

    /**
     * End session via WebSocket
     */
    endSessionWS(ws) {
        ws.send(JSON.stringify({
            action: 'end'
        }));
    }
}

// Example usage in browser
if (typeof window !== 'undefined') {
    window.InterviewClient = InterviewClient;

    // Example: Capture from webcam
    async function startInterview() {
        const client = new InterviewClient('http://localhost:8000');

        // Check health
        const health = await client.healthCheck();
        console.log('API Status:', health.status);

        // Start session
        const sessionId = await client.startSession('candidate_12345');
        console.log('Session started:', sessionId);

        // Get webcam
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        const video = document.createElement('video');
        video.srcObject = stream;
        video.play();

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        // Analyze frames
        setInterval(async () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0);

            const result = await client.analyzeFrameFromCanvas(sessionId, canvas);
            console.log('Risk:', result.risk_score, 'Events:', result.events);

            // Display results
            document.getElementById('risk-score').textContent = result.risk_score;
            document.getElementById('cheating').textContent = result.cheating ? 'YES' : 'NO';
        }, 1000); // 1 FPS
    }
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InterviewClient;
}
