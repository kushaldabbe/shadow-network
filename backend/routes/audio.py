"""Audio API routes — ElevenLabs TTS streaming endpoints."""
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from voice.elevenlabs_client import generate_transmission_audio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/audio", tags=["audio"])


class AudioRequest(BaseModel):
    text: str


@router.post("/generate/{codename}")
async def generate_audio(codename: str, request: AudioRequest):
    """Generate TTS audio for an operative's transmission.
    
    Args:
        codename: Operative codename (determines voice).
        request: AudioRequest with text to convert.
    
    Returns:
        MP3 audio bytes.
    """
    try:
        audio_bytes = generate_transmission_audio(codename.upper(), request.text)
        
        if audio_bytes is None:
            raise HTTPException(
                status_code=503,
                detail="Audio generation unavailable — ElevenLabs API may be down or unconfigured"
            )
        
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"inline; filename={codename}_transmission.mp3"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio generation error for {codename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test/{codename}")
async def test_audio(codename: str):
    """Test audio generation with a short sample text."""
    test_text = f"This is {codename}, secure channel confirmed. Standing by for orders."
    try:
        audio_bytes = generate_transmission_audio(codename.upper(), test_text)
        
        if audio_bytes is None:
            return {"status": "unavailable", "message": "ElevenLabs not configured or API error"}
        
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
        )
    except Exception as e:
        logger.error(f"Audio test error for {codename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
