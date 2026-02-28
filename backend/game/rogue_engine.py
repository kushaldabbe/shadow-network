"""Rogue Engine — autonomous event trigger system that runs every turn end."""
import random
import logging
from datetime import datetime
from typing import List

from config import (
    OPERATIVE_CODENAMES, OPERATIVE_REGIONS,
    LOYALTY_ROGUE_THRESHOLD, LOYALTY_ROGUE_CHANCE,
    TENSION_PRESSURE_THRESHOLD, TENSION_PRESSURE_CHANCE,
    RELATIONSHIP_WARNING_CHANCE,
)
from game.state_manager import (
    load_world_state, save_world_state,
    update_region_tension, update_agency_exposure,
    mark_asset_compromised, add_rogue_event,
)
from game.operative_manager import (
    load_operative, update_loyalty, set_operative_status,
    add_known_compromise, load_all_operatives,
)
from agents.mistral_client import chat_completion

logger = logging.getLogger(__name__)


async def check_autonomous_triggers() -> List[dict]:
    """Run all autonomous trigger checks at end of turn.
    
    Returns:
        List of rogue event dicts that occurred.
    """
    events = []
    operatives = load_all_operatives()
    state = load_world_state()
    
    for codename, operative in operatives.items():
        # Skip non-active operatives
        if operative["current_status"] != "active":
            continue
        
        # 1. Loyalty threshold trigger
        if operative["loyalty"] < LOYALTY_ROGUE_THRESHOLD:
            if random.random() < LOYALTY_ROGUE_CHANCE:
                event = await _trigger_rogue_event(codename, operative, state)
                if event:
                    events.append(event)
                    continue  # Only one event per operative per turn
        
        # 2. External pressure trigger (region tension > threshold)
        region = OPERATIVE_REGIONS.get(codename)
        if region and region in state["regions"]:
            tension = state["regions"][region]["tension"]
            if tension > TENSION_PRESSURE_THRESHOLD:
                if random.random() < TENSION_PRESSURE_CHANCE:
                    event = await _trigger_contact_event(codename, operative, state)
                    if event:
                        events.append(event)
                        continue
        
        # 3. Relationship trigger — operative knows another is compromised
        if operative["known_compromises"]:
            if random.random() < RELATIONSHIP_WARNING_CHANCE:
                event = await _trigger_warning_event(codename, operative, state)
                if event:
                    events.append(event)
    
    # Save any state changes
    state = load_world_state()
    for event in events:
        add_rogue_event(state, event)
    save_world_state(state)
    
    return events


async def _trigger_rogue_event(codename: str, operative: dict, state: dict) -> dict:
    """Trigger a rogue event based on low loyalty.
    
    Randomly selects from: defection_warning, silent_defection, 
    double_agent_activation, unsanctioned_action.
    """
    loyalty = operative["loyalty"]
    
    # Lower loyalty = more severe event type
    if loyalty < 25:
        event_type = random.choice(["silent_defection", "double_agent_activation"])
    elif loyalty < 40:
        event_type = random.choice(["double_agent_activation", "unsanctioned_action", "defection_warning"])
    else:
        event_type = random.choice(["defection_warning", "unsanctioned_action"])
    
    handlers = {
        "defection_warning": _handle_defection_warning,
        "silent_defection": _handle_silent_defection,
        "double_agent_activation": _handle_double_agent,
        "unsanctioned_action": _handle_unsanctioned_action,
    }
    
    handler = handlers.get(event_type, _handle_defection_warning)
    return await handler(codename, operative, state)


async def _handle_defection_warning(codename: str, operative: dict, state: dict) -> dict:
    """Operative warns the Director they're being approached by foreign intel."""
    narration = await _generate_rogue_narration(
        codename, "defection_warning",
        f"{codename} is being approached by a foreign intelligence service and has chosen to warn the Director."
    )
    
    # Effects: loyalty +3 (honest act), exposure +5 (situation is dangerous)
    update_loyalty(codename, 3)
    update_agency_exposure(state, 5)
    save_world_state(state)
    
    return {
        "type": "defection_warning",
        "codename": codename,
        "turn": state["turn"],
        "timestamp": datetime.now().isoformat(),
        "title": f"⚠️ {codename} — DEFECTION WARNING",
        "narration": narration,
        "severity": "warning",
        "effects": {"loyalty_change": 3, "exposure_change": 5},
    }


async def _handle_silent_defection(codename: str, operative: dict, state: dict) -> dict:
    """Operative goes dark — stops responding. Discovered via other agents."""
    narration = await _generate_rogue_narration(
        codename, "silent_defection",
        f"{codename} has gone completely dark. No response on any channel. All contact protocols have failed."
    )
    
    # Effects: status → dark, compromised, all others loyalty -3
    set_operative_status(codename, "dark")
    mark_asset_compromised(state, codename)
    
    for other_codename in OPERATIVE_CODENAMES:
        if other_codename != codename:
            other = load_operative(other_codename)
            if other["current_status"] == "active":
                update_loyalty(other_codename, -3)
                add_known_compromise(other_codename, codename)
    
    save_world_state(state)
    
    return {
        "type": "silent_defection",
        "codename": codename,
        "turn": state["turn"],
        "timestamp": datetime.now().isoformat(),
        "title": f"🔴 {codename} — GONE DARK",
        "narration": narration,
        "severity": "critical",
        "effects": {"status": "dark", "all_loyalty_change": -3, "compromised": True},
    }


async def _handle_double_agent(codename: str, operative: dict, state: dict) -> dict:
    """Operative begins feeding false intel — stays 'active' but compromised."""
    narration = await _generate_rogue_narration(
        codename, "double_agent_activation",
        f"{codename} has been turned. They remain in position but are now feeding false intelligence while passing real intel to a foreign handler."
    )
    
    # Effects: mark compromised but keep status "active" — player doesn't know!
    mark_asset_compromised(state, codename)
    update_agency_exposure(state, 3)
    save_world_state(state)
    
    # NOTE: The player might NOT be informed of this immediately.
    # The event narration should be ambiguous or come via another operative later.
    return {
        "type": "double_agent_activation",
        "codename": codename,
        "turn": state["turn"],
        "timestamp": datetime.now().isoformat(),
        "title": f"⚠️ INTELLIGENCE ANOMALY DETECTED",
        "narration": narration,
        "severity": "warning",
        "effects": {"compromised": True, "exposure_change": 3},
        "hidden": True,  # This event's full truth is hidden from the player
    }


async def _handle_unsanctioned_action(codename: str, operative: dict, state: dict) -> dict:
    """Operative takes an action the Director didn't order."""
    narration = await _generate_rogue_narration(
        codename, "unsanctioned_action",
        f"{codename} has taken an unsanctioned action in the field — acting without authorization."
    )
    
    # Effects: loyalty -5, exposure +10, tension +8
    update_loyalty(codename, -5)
    update_agency_exposure(state, 10)
    
    region = OPERATIVE_REGIONS.get(codename)
    if region:
        update_region_tension(state, region, 8)
    
    save_world_state(state)
    
    return {
        "type": "unsanctioned_action",
        "codename": codename,
        "turn": state["turn"],
        "timestamp": datetime.now().isoformat(),
        "title": f"🔴 {codename} — UNSANCTIONED ACTION",
        "narration": narration,
        "severity": "critical",
        "effects": {"loyalty_change": -5, "exposure_change": 10, "tension_change": 8},
    }


async def _trigger_contact_event(codename: str, operative: dict, state: dict) -> dict:
    """External pressure event — foreign intel reaches out due to high regional tension."""
    narration = await _generate_rogue_narration(
        codename, "external_contact",
        f"High regional tension has drawn attention to {codename}'s location. A foreign intelligence service has made contact."
    )
    
    update_loyalty(codename, -3)
    update_agency_exposure(state, 3)
    save_world_state(state)
    
    return {
        "type": "external_contact",
        "codename": codename,
        "turn": state["turn"],
        "timestamp": datetime.now().isoformat(),
        "title": f"⚠️ {codename} — FOREIGN CONTACT DETECTED",
        "narration": narration,
        "severity": "warning",
        "effects": {"loyalty_change": -3, "exposure_change": 3},
    }


async def _trigger_warning_event(codename: str, operative: dict, state: dict) -> dict:
    """Operative who knows another is compromised reacts — may warn the Director."""
    compromised = operative["known_compromises"][0]
    narration = await _generate_rogue_narration(
        codename, "compromise_warning",
        f"{codename} has learned that {compromised} may be compromised and is deciding whether to warn the Director."
    )
    
    # Small loyalty boost for warning
    update_loyalty(codename, 2)
    save_world_state(state)
    
    return {
        "type": "compromise_warning",
        "codename": codename,
        "turn": state["turn"],
        "timestamp": datetime.now().isoformat(),
        "title": f"⚠️ {codename} — OPERATIVE WARNING",
        "narration": narration,
        "severity": "warning",
        "effects": {"loyalty_change": 2, "warned_about": compromised},
    }


async def _generate_rogue_narration(codename: str, event_type: str, context: str) -> str:
    """Generate dramatic narrative text for a rogue event using Mistral.
    
    Args:
        codename: Operative codename.
        event_type: Type of rogue event.
        context: Brief context for the narration.
    
    Returns:
        Dramatic narrative text string.
    """
    system_prompt = (
        "You are a narrator for a Cold War spy thriller game. "
        "Generate a short, dramatic, tense narration (2-3 paragraphs max) for a rogue event. "
        "Write it like an intelligence alert or field report — urgent, professional, with dramatic tension. "
        "Do NOT use character dialogue. Write in third person from the agency's perspective. "
        "Keep it under 150 words."
    )
    
    user_message = (
        f"Operative codename: {codename}\n"
        f"Event type: {event_type}\n"
        f"Context: {context}\n\n"
        f"Generate the rogue event narration."
    )
    
    try:
        narration = await chat_completion(system_prompt, user_message, temperature=0.8)
        return narration
    except Exception as e:
        logger.error(f"Rogue narration generation failed: {e}")
        # Fallback narration
        fallbacks = {
            "defection_warning": f"ALERT: {codename} has reported being approached by an unknown foreign intelligence operative. The contact attempted to recruit {codename} using undisclosed leverage. {codename} has self-reported this contact per protocol. Assessment: volatile situation requiring immediate Director attention.",
            "silent_defection": f"CRITICAL: All communication channels with {codename} have gone silent. Last contact was 6 hours ago. Extraction team on standby. All assets in the region should assume compromise. This is not a drill.",
            "double_agent_activation": f"ANOMALY: Pattern analysis has flagged inconsistencies in recent intelligence from the field. Multiple data points suggest possible information manipulation. Source cannot be confirmed. Recommend enhanced verification protocols on all incoming intelligence.",
            "unsanctioned_action": f"BREACH: {codename} has conducted an unauthorized field operation without Director approval. Details are still emerging but initial reports suggest significant operational exposure. Regional assets may be at risk.",
            "external_contact": f"WARNING: Signals intelligence has detected an unauthorized communication channel near {codename}'s operating area. A foreign intelligence service appears to have made contact. {codename}'s response is unknown.",
            "compromise_warning": f"INTEL: An operative has flagged concerns about the reliability of a network asset. Internal review recommended. Details classified pending Director assessment.",
        }
        return fallbacks.get(event_type, f"ALERT: Anomalous activity detected involving {codename}. Details pending analysis.")
