"""ElevenLabs TTS client — generates operative voice transmissions."""
import hashlib
import logging
from pathlib import Path
from typing import Optional

from elevenlabs.client import ElevenLabs
from config import ELEVENLABS_API_KEY, ELEVENLABS_MODEL, OPERATIVE_VOICES, VOICE_CACHE_DIR

logger = logging.getLogger(__name__)

# Initialize ElevenLabs client
client = ElevenLabs(api_key=ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else None

# Ensure cache directory exists
VOICE_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _get_cache_path(codename: str, text: str) -> Path:
    """Generate a cache file path based on codename and text hash."""
    text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
    return VOICE_CACHE_DIR / f"{codename}_{text_hash}.mp3"


def generate_transmission_audio(codename: str, text: str) -> Optional[bytes]:
    """Generate TTS audio for an operative's transmission.
    
    Args:
        codename: Operative codename (used to select voice).
        text: The transmission text to convert to speech.
    
    Returns:
        Audio bytes (mp3), or None if generation fails.
    """
    if not client:
        logger.warning("ElevenLabs client not initialized — no API key")
        return None
    
    voice_id = OPERATIVE_VOICES.get(codename)
    if not voice_id:
        logger.error(f"No voice ID configured for {codename}")
        return None
    
    # Check cache first
    cache_path = _get_cache_path(codename, text)
    if cache_path.exists():
        logger.info(f"Cache hit for {codename} audio")
        return cache_path.read_bytes()
    
    try:
        # Generate audio
        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id=ELEVENLABS_MODEL,
        )
        
        # Collect audio bytes from generator
        audio_bytes = b"".join(audio_generator)
        
        # Cache it
        cache_path.write_bytes(audio_bytes)
        logger.info(f"Generated and cached audio for {codename} ({len(audio_bytes)} bytes)")
        
        return audio_bytes
    except Exception as e:
        logger.error(f"ElevenLabs TTS failed for {codename}: {e}")
        return None


def get_cached_audio(codename: str, text: str) -> Optional[bytes]:
    """Get cached audio if it exists.
    
    Args:
        codename: Operative codename.
        text: The transmission text.
    
    Returns:
        Cached audio bytes, or None.
    """
    cache_path = _get_cache_path(codename, text)
    if cache_path.exists():
        return cache_path.read_bytes()
    return None


def clear_cache():
    """Clear all cached audio files."""
    for f in VOICE_CACHE_DIR.glob("*.mp3"):
        f.unlink()
    logger.info("Voice cache cleared")
