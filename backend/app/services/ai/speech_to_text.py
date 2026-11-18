import io
import time
from typing import Dict, Any, Optional
from app.core.logging import logger


class SpeechToTextService:
    """
    Speech-to-Text service using free, no-API-key solutions:
    1. Browser WebSpeech live transcript (sent as form field) — most reliable
    2. Google Free STT via SpeechRecognition library (no API key needed)
    3. Empty string fallback (honest — never fakes a transcript)
    """

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str = "audio.webm",
        fallback_transcript: Optional[str] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()

        # ── Priority 1: Browser WebSpeech live transcript ─────────────────────
        # This is captured in real-time by the browser's SpeechRecognition API
        # and sent alongside the audio blob — most accurate for English/Hindi.
        if fallback_transcript and len(fallback_transcript.strip()) > 3:
            return {
                "transcript": fallback_transcript.strip(),
                "latency_seconds": round(time.time() - start_time, 2),
                "provider": "Browser WebSpeech API (Live Recognition)",
            }

        # ── Priority 2: Google Free STT via speech_recognition library ────────
        # Uses Google's free Speech Recognition endpoint (no API key needed).
        # Note: browser sends WebM audio; the library handles it via AudioFile.
        try:
            import speech_recognition as sr  # noqa: PLC0415

            recognizer = sr.Recognizer()
            audio_io = io.BytesIO(audio_bytes)
            with sr.AudioFile(audio_io) as source:
                audio_data = recognizer.record(source)
            transcript = recognizer.recognize_google(audio_data)
            if transcript:
                return {
                    "transcript": transcript,
                    "latency_seconds": round(time.time() - start_time, 2),
                    "provider": "Google Speech Recognition (Free)",
                }
        except ImportError:
            logger.debug("speech_recognition not installed; skipping Google STT.")
        except Exception as e:
            logger.warning(f"Google STT failed ({type(e).__name__}): {e}")

        # ── Priority 3: Honest empty fallback ─────────────────────────────────
        # If neither source produced a transcript we return "" so the caller
        # can substitute "I could not provide an answer." downstream.
        return {
            "transcript": "",
            "latency_seconds": round(time.time() - start_time, 2),
            "provider": "No STT available",
        }


stt_service = SpeechToTextService()
