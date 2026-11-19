import io
import os
import sys
import time
import tempfile
import subprocess
import shutil
from typing import Dict, Any, Optional
from app.core.logging import logger


def _find_ffmpeg() -> Optional[str]:
    """Find ffmpeg executable, checking PATH and common Windows install locations."""
    # 1. Check if already on PATH
    found = shutil.which("ffmpeg")
    if found:
        return found

    # 2. Check common Windows WinGet / Chocolatey / manual install locations
    candidate_dirs = []
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    if local_appdata:
        winget_dir = os.path.join(local_appdata, "Microsoft", "WinGet", "Packages")
        if os.path.isdir(winget_dir):
            for entry in os.listdir(winget_dir):
                if "ffmpeg" in entry.lower():
                    bin_dir = None
                    pkg_path = os.path.join(winget_dir, entry)
                    # Look for bin/ subdirectory inside the package
                    for root, dirs, files in os.walk(pkg_path):
                        if "ffmpeg.exe" in files:
                            bin_dir = root
                            break
                    if bin_dir:
                        candidate_dirs.append(bin_dir)

    # Also check user PATH from registry (may not be in current process env)
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
            user_path = winreg.QueryValueEx(key, "Path")[0]
            for p in user_path.split(";"):
                p = p.strip().replace("%USERPROFILE%", os.path.expanduser("~"))
                if p and os.path.isfile(os.path.join(p, "ffmpeg.exe")):
                    candidate_dirs.append(p)
    except Exception:
        pass

    for d in candidate_dirs:
        ffmpeg_path = os.path.join(d, "ffmpeg.exe") if sys.platform == "win32" else os.path.join(d, "ffmpeg")
        if os.path.isfile(ffmpeg_path):
            # Add to current process PATH so pydub also finds it
            os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
            logger.info(f"Found ffmpeg at: {ffmpeg_path}")
            return ffmpeg_path

    return None


# Discover ffmpeg once at module load
_FFMPEG_PATH = _find_ffmpeg()


class SpeechToTextService:
    """
    Speech-to-Text service using free, no-API-key solutions:
    1. Browser WebSpeech live transcript (sent as form field) — most reliable
    2. Convert WebM→WAV via ffmpeg, then Google Free STT via SpeechRecognition
    3. Empty string fallback (honest — never fakes a transcript)
    """

    def _convert_to_wav(self, audio_bytes: bytes, filename: str = "audio.webm") -> Optional[bytes]:
        """Convert any audio (WebM/MP3/OGG/M4A/etc.) to WAV so speech_recognition can read it.
        Tries ffmpeg CLI first, then falls back to pydub."""
        tmp_in = None
        try:
            ext = os.path.splitext(filename)[1].lower() if filename else ".webm"
            if not ext or ext == ".wav":
                ext = ".webm"
            tmp_in = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
            tmp_in.write(audio_bytes)
            tmp_in.close()

            tmp_out_path = tmp_in.name + ".wav"

            # ── Method 1: Direct ffmpeg CLI ───────────────────────────────────
            ffmpeg_cmd = _FFMPEG_PATH or "ffmpeg"
            try:
                result = subprocess.run(
                    [
                        ffmpeg_cmd, "-y", "-i", tmp_in.name,
                        "-ar", "16000", "-ac", "1", "-f", "wav", tmp_out_path,
                    ],
                    capture_output=True, timeout=15,
                )
                if result.returncode == 0:
                    with open(tmp_out_path, "rb") as f:
                        wav_bytes = f.read()
                    try:
                        os.unlink(tmp_out_path)
                    except OSError:
                        pass
                    return wav_bytes
                else:
                    logger.warning(f"ffmpeg CLI failed: {result.stderr.decode(errors='replace')[:200]}")
            except FileNotFoundError:
                logger.debug("ffmpeg not found on PATH; trying pydub fallback.")
            except Exception as e:
                logger.warning(f"ffmpeg CLI error: {e}")

            # ── Method 2: pydub (uses ffmpeg/avconv under the hood) ───────────
            try:
                from pydub import AudioSegment  # noqa: PLC0415
                audio_seg = AudioSegment.from_file(tmp_in.name)
                wav_io = io.BytesIO()
                audio_seg.set_frame_rate(16000).set_channels(1).export(wav_io, format="wav")
                return wav_io.getvalue()
            except ImportError:
                logger.debug("pydub not installed; skipping pydub conversion.")
            except Exception as e:
                logger.warning(f"pydub conversion failed: {e}")

            return None
        except Exception as e:
            logger.warning(f"Audio→WAV conversion error: {e}")
            return None
        finally:
            if tmp_in:
                try:
                    os.unlink(tmp_in.name)
                except OSError:
                    pass

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
        # Convert audio to 16kHz mono WAV first via ffmpeg, then feed to Google Free STT.
        try:
            import speech_recognition as sr  # noqa: PLC0415

            # If not a pure uncompressed WAV, convert to standard WAV
            wav_bytes = self._convert_to_wav(audio_bytes, filename=filename)
            audio_data_bytes = wav_bytes if wav_bytes else audio_bytes

            recognizer = sr.Recognizer()
            audio_io = io.BytesIO(audio_data_bytes)
            with sr.AudioFile(audio_io) as source:
                audio_data = recognizer.record(source)
            transcript = recognizer.recognize_google(audio_data)
            if transcript:
                return {
                    "transcript": transcript,
                    "latency_seconds": round(time.time() - start_time, 2),
                    "provider": "Google Speech Recognition (Free via ffmpeg)",
                }
        except ImportError:
            logger.debug("speech_recognition not installed; skipping Google STT.")
        except Exception as e:
            logger.warning(f"Google STT failed ({type(e).__name__}): {e}")

        # ── Priority 3: Honest empty fallback ─────────────────────────────────
        # If neither source produced a transcript we return "" so the caller
        # knows no speech was captured.
        return {
            "transcript": "",
            "latency_seconds": round(time.time() - start_time, 2),
            "provider": "No STT available",
        }


stt_service = SpeechToTextService()
