"""
Audio Monitoring Module
Detects multiple voices, whispering, background noise, and suspicious sounds
"""
import numpy as np
import threading
import queue
from collections import deque


class AudioMonitor:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.is_monitoring = False
        self.audio_history = deque(maxlen=100)
        
        # Detection thresholds
        self.SILENCE_THRESHOLD = 500
        self.WHISPER_THRESHOLD = 1500
        self.NORMAL_THRESHOLD = 3000
        
        # Event counters
        self.silence_count = 0
        self.whisper_count = 0
        self.loud_noise_count = 0
        self.multiple_voice_detected = False
        
    def calculate_audio_level(self, audio_data):
        """Calculate RMS audio level"""
        if audio_data is None or len(audio_data) == 0:
            return 0
        
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_array**2))
        return rms
    
    def detect_whisper(self, audio_level):
        """Detect whispering (low volume speech)"""
        if self.SILENCE_THRESHOLD < audio_level < self.WHISPER_THRESHOLD:
            self.whisper_count += 1
            return True
        return False
    
    def detect_silence_pattern(self, audio_history):
        """Detect suspicious silence patterns (muting/unmuting)"""
        if len(audio_history) < 20:
            return False
        
        recent = list(audio_history)[-20:]
        silent_frames = sum(1 for level in recent if level < self.SILENCE_THRESHOLD)
        
        # More than 50% silence is suspicious
        if silent_frames > 10:
            return True
        return False
    
    def detect_background_noise(self, audio_level):
        """Detect unusual background noise"""
        if audio_level > self.NORMAL_THRESHOLD:
            self.loud_noise_count += 1
            return True
        return False
    
    def analyze_audio_frame(self, audio_data):
        """Analyze single audio frame"""
        level = self.calculate_audio_level(audio_data)
        self.audio_history.append(level)
        
        events = []
        
        # Check for whisper
        if self.detect_whisper(level):
            events.append("WHISPER_DETECTED")
        
        # Check for background noise
        if self.detect_background_noise(level):
            events.append("LOUD_NOISE")
        
        # Check silence pattern
        if self.detect_silence_pattern(self.audio_history):
            events.append("SUSPICIOUS_SILENCE")
        
        return events, level
    
    def get_audio_summary(self):
        """Get summary of audio analysis"""
        return {
            'whisper_count': self.whisper_count,
            'loud_noise_count': self.loud_noise_count,
            'silence_count': self.silence_count,
            'avg_level': np.mean(list(self.audio_history)) if self.audio_history else 0
        }
    
    def reset(self):
        """Reset audio monitoring state"""
        self.whisper_count = 0
        self.loud_noise_count = 0
        self.silence_count = 0
        self.audio_history.clear()
