"""Configuration for Shadow Network backend."""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# Mistral Config
MISTRAL_MODEL = "mistral-large-latest"

# ElevenLabs Config
ELEVENLABS_MODEL = "eleven_multilingual_v2"

# Voice IDs per operative (placeholder — replace with real IDs)
OPERATIVE_VOICES = {
    "NIGHTHAWK": "PleK417YVMP2SUWm8Btb",   # Male, calm
    "CEDAR": "IKne3meq5aSn9XLyUdCD",        # Male, clipped
    "GHOST": "TX3LPaxmHKxFdv7VOQHJ",        # Male, nervous
    "SABLE": "XB0fDUnXU5powFXDhCwa",        # Female, intense
    "LOTUS": "pFZP5JQG7iQjIQuC4Bku",        # Female, measured
}

# Operative codenames
OPERATIVE_CODENAMES = ["NIGHTHAWK", "CEDAR", "GHOST", "SABLE", "LOTUS"]

# Operative regions mapping
OPERATIVE_REGIONS = {
    "NIGHTHAWK": "middle_east",
    "CEDAR": "middle_east",
    "GHOST": "south_asia",
    "SABLE": "eastern_europe",
    "LOTUS": "east_asia",
}

# Rogue engine thresholds
LOYALTY_ROGUE_THRESHOLD = 50
LOYALTY_ROGUE_CHANCE = 0.30
TENSION_PRESSURE_THRESHOLD = 80
TENSION_PRESSURE_CHANCE = 0.20
RELATIONSHIP_WARNING_CHANCE = 0.40

# Game over conditions
EXPOSURE_GAME_OVER = 100
TRUST_GAME_OVER = 0

# Paths
import pathlib
BASE_DIR = pathlib.Path(__file__).parent
MEMORY_DIR = BASE_DIR / "memory"
MEMORY_INITIAL_DIR = BASE_DIR / "memory_initial"
STATE_DIR = BASE_DIR / "state"
STATE_INITIAL_DIR = BASE_DIR / "state_initial"
VOICE_CACHE_DIR = BASE_DIR / "voice" / "cache"
PROMPTS_DIR = BASE_DIR / "agents" / "prompts"
