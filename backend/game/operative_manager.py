"""Operative Manager — CRUD operations for operative memory/state files."""
import json
import logging
import random
from typing import Optional
from config import MEMORY_DIR, OPERATIVE_CODENAMES

logger = logging.getLogger(__name__)


def load_operative(codename: str) -> dict:
    """Load an operative's memory/state from JSON.
    
    Args:
        codename: Operative codename (e.g. 'NIGHTHAWK').
    
    Returns:
        Operative data dict.
    """
    path = MEMORY_DIR / f"{codename}.json"
    with open(path, "r") as f:
        return json.load(f)


def save_operative(codename: str, data: dict) -> None:
    """Save an operative's memory/state to JSON.
    
    Args:
        codename: Operative codename.
        data: Full operative data dict.
    """
    path = MEMORY_DIR / f"{codename}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Operative {codename} state saved (loyalty={data.get('loyalty', '?')})")


def load_all_operatives() -> dict:
    """Load all operative data.
    
    Returns:
        Dict mapping codename -> operative data.
    """
    operatives = {}
    for codename in OPERATIVE_CODENAMES:
        try:
            operatives[codename] = load_operative(codename)
        except FileNotFoundError:
            logger.warning(f"Operative file not found: {codename}")
    return operatives


def log_mission(codename: str, mission: dict) -> dict:
    """Log a completed mission to an operative's memory.
    
    Args:
        codename: Operative codename.
        mission: Mission record with fields:
            - id: str
            - turn: int
            - order_received: str
            - decision: str (comply/partial/deceive/rogue)
            - reason_hidden: str
            - reported_to_director: str
            - outcome: str
    
    Returns:
        Updated operative data.
    """
    data = load_operative(codename)
    data["missions"].append(mission)
    save_operative(codename, data)
    logger.info(f"Mission logged for {codename}: {mission.get('id', 'unknown')}")
    return data


def update_loyalty(codename: str, delta: int) -> dict:
    """Update an operative's loyalty score, clamped 0-100.
    
    Args:
        codename: Operative codename.
        delta: Amount to add (positive) or subtract (negative).
    
    Returns:
        Updated operative data.
    """
    data = load_operative(codename)
    old = data["loyalty"]
    data["loyalty"] = max(0, min(100, old + delta))
    save_operative(codename, data)
    logger.info(f"{codename} loyalty: {old} → {data['loyalty']}")
    return data


def update_relationship(codename: str, target: str, description: str) -> dict:
    """Update the relationship between two operatives.
    
    Args:
        codename: The operative whose memory to update.
        target: The other operative's codename.
        description: New relationship description.
    
    Returns:
        Updated operative data.
    """
    data = load_operative(codename)
    data["relationships"][target] = description
    save_operative(codename, data)
    logger.info(f"{codename}'s relationship with {target} updated: {description}")
    return data


def add_known_compromise(codename: str, compromised_codename: str) -> dict:
    """Record that an operative knows another is compromised.
    
    Args:
        codename: The operative learning the information.
        compromised_codename: The compromised operative.
    
    Returns:
        Updated operative data.
    """
    data = load_operative(codename)
    if compromised_codename not in data["known_compromises"]:
        data["known_compromises"].append(compromised_codename)
        save_operative(codename, data)
        logger.info(f"{codename} now knows {compromised_codename} is compromised")
    return data


def set_operative_status(codename: str, status: str) -> dict:
    """Set operative status (active, dark, compromised, extracted).
    
    Args:
        codename: Operative codename.
        status: New status string.
    
    Returns:
        Updated operative data.
    """
    data = load_operative(codename)
    old = data["current_status"]
    data["current_status"] = status
    save_operative(codename, data)
    logger.info(f"{codename} status: {old} → {status}")
    return data


def get_operative_public_info(codename: str) -> dict:
    """Get public info for an operative (what the player/frontend sees).
    
    Signal quality is a noisy proxy for loyalty — the player shouldn't see exact loyalty.
    """
    data = load_operative(codename)
    loyalty = data["loyalty"]
    
    # Signal quality: loyalty ± random noise (±10), clamped 0-100
    noise = random.randint(-10, 10)
    signal_quality = max(0, min(100, loyalty + noise))
    
    return {
        "codename": data["codename"],
        "location": data["location"],
        "region": data["region"],
        "status": data["current_status"],
        "signal_quality": signal_quality,
        "mission_count": len(data["missions"]),
    }


def get_all_operatives_public() -> list:
    """Get public info for all operatives."""
    return [get_operative_public_info(cn) for cn in OPERATIVE_CODENAMES]
