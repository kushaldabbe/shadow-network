"""Decision Engine — processes operative responses and player decisions."""
import logging
from game.state_manager import (
    load_world_state, save_world_state,
    update_region_tension, update_agency_exposure, update_director_trust,
    mark_asset_compromised, add_mission_to_log,
)
from game.operative_manager import (
    load_operative, update_loyalty, log_mission, set_operative_status,
    add_known_compromise,
)
from config import OPERATIVE_REGIONS

logger = logging.getLogger(__name__)


def process_operative_response(codename: str, order: str, response_data: dict) -> dict:
    """Process an operative's response — update world state, loyalty, log mission.
    
    Args:
        codename: Operative codename.
        order: Original order text.
        response_data: Dict from call_operative() with response, hidden_meta, etc.
    
    Returns:
        Dict with summary of all state changes applied.
    """
    hidden = response_data.get("hidden_meta", {})
    decision = hidden.get("decision", "comply")
    loyalty_shift = hidden.get("loyalty_shift", 0)
    tension_impact = hidden.get("tension_impact", 0)
    exposure_impact = hidden.get("exposure_impact", 0)
    reason = hidden.get("reason", "")
    
    state = load_world_state()
    changes = {
        "codename": codename,
        "decision": decision,
        "loyalty_shift": loyalty_shift,
        "tension_impact": tension_impact,
        "exposure_impact": exposure_impact,
    }
    
    # 1. Update loyalty
    if loyalty_shift != 0:
        update_loyalty(codename, loyalty_shift)
    
    # 2. Apply additional loyalty effects based on decision
    decision_loyalty_effects = {
        "comply": 1,      # Small trust boost for compliance
        "partial": -1,    # Slight suspicion
        "deceive": -2,    # Will be noticed eventually
        "exceed": -2,     # Unauthorized action
        "rogue": -5,      # Major breach
    }
    extra_shift = decision_loyalty_effects.get(decision, 0)
    if extra_shift != 0:
        update_loyalty(codename, extra_shift)
        changes["extra_loyalty_shift"] = extra_shift
    
    # 3. Update region tension
    region = OPERATIVE_REGIONS.get(codename)
    if region and tension_impact != 0:
        update_region_tension(state, region, tension_impact)
    
    # 4. Update agency exposure
    if exposure_impact != 0:
        update_agency_exposure(state, exposure_impact)
    
    # 5. Director trust adjustments
    if decision in ("deceive", "rogue"):
        # Deceptive operatives erode trust over time (even if Director doesn't know yet)
        update_director_trust(state, -2)
        changes["trust_impact"] = -2
    elif decision == "comply":
        update_director_trust(state, 1)
        changes["trust_impact"] = 1
    
    # 6. Handle rogue decisions 
    if decision == "rogue":
        operative_data = load_operative(codename)
        if operative_data["loyalty"] < 30:
            set_operative_status(codename, "dark")
            mark_asset_compromised(state, codename)
            changes["status_change"] = "dark"
    
    # 7. Log mission to operative memory
    mission_record = {
        "id": f"mission_{state['turn']}_{codename}",
        "turn": state["turn"],
        "order_received": order,
        "decision": decision,
        "reason_hidden": reason,
        "reported_to_director": response_data.get("response", "")[:200],
        "outcome": f"Decision: {decision}, loyalty shift: {loyalty_shift + extra_shift}",
    }
    log_mission(codename, mission_record)
    
    # 8. Log mission to global state
    add_mission_to_log(state, {
        "turn": state["turn"],
        "operative": codename,
        "order": order,
        "response_summary": response_data.get("response", "")[:150],
        "mission_type": "field_operation",
    })
    
    # Save updated world state
    save_world_state(state)
    
    logger.info(f"Processed {codename} response: decision={decision}")
    return changes


def process_event_response(director_action: str, event: dict) -> dict:
    """Process the Director's response to a world event.
    
    Args:
        director_action: The action chosen by the Director.
        event: The world event dict.
    
    Returns:
        Dict with action taken and any state changes.
    """
    state = load_world_state()
    
    # The Director's engagement with events builds trust
    update_director_trust(state, 2)
    
    save_world_state(state)
    
    return {
        "action_taken": director_action,
        "event_title": event.get("event_title", "Unknown Event"),
        "trust_change": 2,
    }


def handle_extraction_order(codename: str) -> dict:
    """Handle a Director's order to extract an operative.
    
    Extraction:
    - Sets operative status to 'extracted'
    - Increases exposure slightly (extraction operations are risky)
    - Removes from compromised if was compromised
    
    Args:
        codename: Operative to extract.
    
    Returns:
        Summary dict.
    """
    state = load_world_state()
    
    set_operative_status(codename, "extracted")
    update_agency_exposure(state, 5)
    
    # Remove from compromised list if present
    if codename in state["compromised_assets"]:
        state["compromised_assets"].remove(codename)
    
    save_world_state(state)
    
    return {
        "codename": codename,
        "action": "extracted",
        "exposure_increase": 5,
        "message": f"{codename} has been extracted from the field. Cover identities burned. Network in {OPERATIVE_REGIONS.get(codename, 'unknown')} region will need to be rebuilt."
    }
