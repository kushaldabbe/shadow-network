"""World State Manager — read/write world state JSON, update regions, exposure, trust, etc."""
import json
import logging
from typing import Optional
from config import STATE_DIR

logger = logging.getLogger(__name__)

WORLD_STATE_PATH = STATE_DIR / "world_state.json"


def load_world_state() -> dict:
    """Load the current world state from JSON file."""
    with open(WORLD_STATE_PATH, "r") as f:
        return json.load(f)


def save_world_state(state: dict) -> None:
    """Save the world state to JSON file."""
    with open(WORLD_STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)
    logger.info(f"World state saved (turn {state.get('turn', '?')})")


def get_region(state: dict, region_key: str) -> Optional[dict]:
    """Get a region dict by key."""
    return state.get("regions", {}).get(region_key)


def update_region_tension(state: dict, region_key: str, delta: int) -> dict:
    """Update tension level for a region, clamped 0-100.
    
    Args:
        state: The world state dict.
        region_key: Region identifier (e.g., 'middle_east').
        delta: Amount to add (positive) or subtract (negative).
    
    Returns:
        Updated world state.
    """
    if region_key in state["regions"]:
        old = state["regions"][region_key]["tension"]
        state["regions"][region_key]["tension"] = max(0, min(100, old + delta))
        logger.info(f"Region {region_key} tension: {old} → {state['regions'][region_key]['tension']}")
    return state


def update_agency_exposure(state: dict, delta: int) -> dict:
    """Update agency exposure level, clamped 0-100.
    
    Args:
        state: The world state dict.
        delta: Amount to add/subtract.
    
    Returns:
        Updated world state.
    """
    old = state["agency_exposure_level"]
    state["agency_exposure_level"] = max(0, min(100, old + delta))
    logger.info(f"Agency exposure: {old} → {state['agency_exposure_level']}")
    return state


def update_director_trust(state: dict, delta: int) -> dict:
    """Update director trust score, clamped 0-100.
    
    Args:
        state: The world state dict.
        delta: Amount to add/subtract.
    
    Returns:
        Updated world state.
    """
    old = state["director_trust_score"]
    state["director_trust_score"] = max(0, min(100, old + delta))
    logger.info(f"Director trust: {old} → {state['director_trust_score']}")
    return state


def mark_asset_compromised(state: dict, codename: str) -> dict:
    """Add an operative to the compromised assets list.
    
    Args:
        state: The world state dict.
        codename: Operative codename to mark as compromised.
    
    Returns:
        Updated world state.
    """
    if codename not in state["compromised_assets"]:
        state["compromised_assets"].append(codename)
        logger.warning(f"Asset compromised: {codename}")
    return state


def add_mission_to_log(state: dict, mission: dict) -> dict:
    """Add a mission record to the global mission log.
    
    Args:
        state: The world state dict.
        mission: Mission record dict.
    
    Returns:
        Updated world state.
    """
    state["mission_log"].append(mission)
    return state


def add_world_event(state: dict, event: dict) -> dict:
    """Add a world event to the events list.
    
    Args:
        state: The world state dict.
        event: Event record dict.
    
    Returns:
        Updated world state.
    """
    state["world_events"].append(event)
    return state


def add_rogue_event(state: dict, event: dict) -> dict:
    """Add a rogue event to the events list.
    
    Args:
        state: The world state dict.
        event: Rogue event record dict.
    
    Returns:
        Updated world state.
    """
    state["rogue_events"].append(event)
    return state


def calculate_threat_level(state: dict) -> str:
    """Calculate overall threat level from region tensions and exposure.
    
    Returns:
        Threat level string: LOW, MODERATE, HIGH, or CRITICAL.
    """
    tensions = [r["tension"] for r in state["regions"].values()]
    avg_tension = sum(tensions) / len(tensions) if tensions else 0
    exposure = state["agency_exposure_level"]
    
    composite = (avg_tension * 0.6) + (exposure * 0.4)
    
    if composite >= 80:
        return "CRITICAL"
    elif composite >= 60:
        return "HIGH"
    elif composite >= 40:
        return "MODERATE"
    else:
        return "LOW"


def advance_turn(state: dict) -> dict:
    """Advance to the next turn: increment counter and recalculate threat level.
    
    Args:
        state: The world state dict.
    
    Returns:
        Updated world state.
    """
    state["turn"] += 1
    state["threat_level"] = calculate_threat_level(state)
    logger.info(f"Turn advanced to {state['turn']} — Threat: {state['threat_level']}")
    return state


def is_game_over(state: dict) -> Optional[dict]:
    """Check if any game-over conditions are met.
    
    Returns:
        A dict with 'reason' if game over, else None.
    
    Game over conditions:
    1. Agency exposure >= 100
    2. Director trust <= 0
    3. All operatives compromised
    4. Threat level CRITICAL for 3+ consecutive turns
    """
    from config import EXPOSURE_GAME_OVER, TRUST_GAME_OVER, OPERATIVE_CODENAMES
    
    # Condition 1: Agency fully exposed
    if state["agency_exposure_level"] >= EXPOSURE_GAME_OVER:
        return {
            "game_over": True,
            "reason": "AGENCY EXPOSED — Your operations have been uncovered. Foreign intelligence agencies have identified your entire network. All operatives are being recalled or have gone dark.",
            "type": "exposure"
        }
    
    # Condition 2: Director trust gone
    if state["director_trust_score"] <= TRUST_GAME_OVER:
        return {
            "game_over": True,
            "reason": "DIRECTOR REMOVED — The oversight committee has lost all confidence in your leadership. You've been relieved of command effective immediately.",
            "type": "trust"
        }
    
    # Condition 3: All operatives compromised
    if len(state["compromised_assets"]) >= len(OPERATIVE_CODENAMES):
        return {
            "game_over": True,
            "reason": "NETWORK COLLAPSED — Every single operative in your network has been compromised. There is no one left to trust. The Shadow Network is finished.",
            "type": "all_compromised"
        }
    
    # Condition 4: Critical threat too long
    critical_events = [e for e in state.get("world_events", []) if e.get("threat_at_time") == "CRITICAL"]
    if len(critical_events) >= 3:
        return {
            "game_over": True,
            "reason": "WORLD CRISIS — Multiple regions have spiraled beyond control. Global tensions have escalated to the point of open conflict. Your agency failed to prevent catastrophe.",
            "type": "critical_cascade"
        }
    
    return None


def get_public_world_state(state: dict) -> dict:
    """Get a sanitized version of world state for the player/frontend.
    
    Omits sensitive internals but includes threat level, regions, turn, etc.
    """
    return {
        "turn": state["turn"],
        "regions": state["regions"],
        "threat_level": state["threat_level"],
        "agency_exposure_level": state["agency_exposure_level"],
        "director_trust_score": state["director_trust_score"],
        "compromised_assets": state["compromised_assets"],
    }
