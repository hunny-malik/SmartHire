import time
import base64
from typing import Dict, Any, Optional
from app.core.logging import logger

class TextToSpeechService:
    """
    Text-to-Speech abstraction with Edge-TTS / WebSpeech synthesis capabilities.
    """
    async def synthesize(self, text: str, language: str = "English") -> Dict[str, Any]:
        start_time = time.time()
        
        # Select voice based on language
        voice = "en-US-JennyNeural"
        if language.lower() in ["hindi", "hinglish"]:
            voice = "hi-IN-SwaraNeural"

        # Edge-TTS attempt if package installed
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            b64_audio = base64.b64encode(audio_data).decode("utf-8")
            latency = time.time() - start_time
            return {
                "audio_base64": b64_audio,
                "mime_type": "audio/mp3",
                "voice": voice,
                "latency_seconds": round(latency, 2),
                "provider": "Edge-TTS (Neural)"
            }
        except Exception:
            # Fallback signaling client browser SpeechSynthesis API
            latency = time.time() - start_time
            return {
                "audio_base64": None, # Indicates frontend SpeechSynthesis / WebAudio fallback
                "text": text,
                "voice": voice,
                "latency_seconds": round(latency, 2),
                "provider": "Browser WebSpeech API Fallback"
            }

tts_service = TextToSpeechService()
