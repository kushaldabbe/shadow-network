"""Utility to create/restore backups of game state and memory files."""
import json
import shutil
import logging
from config import MEMORY_DIR, MEMORY_INITIAL_DIR, STATE_DIR, STATE_INITIAL_DIR, OPERATIVE_CODENAMES

logger = logging.getLogger(__name__)


def reset_game_state():
    """Reset all game state and memory files to initial values."""
    # Reset world state
    for filename in ["world_state.json", "ground_truth.json", "covert_messages.json"]:
        src = STATE_INITIAL_DIR / filename
        dst = STATE_DIR / filename
        if src.exists():
            shutil.copy2(src, dst)
            logger.info(f"Reset {filename}")

    # Reset operative memories
    for codename in OPERATIVE_CODENAMES:
        src = MEMORY_INITIAL_DIR / f"{codename}.json"
        dst = MEMORY_DIR / f"{codename}.json"
        if src.exists():
            shutil.copy2(src, dst)
            logger.info(f"Reset {codename} memory")

    logger.info("Game state fully reset to initial values.")
