"""Orchestrator Agent — mission control, event generation, order routing, intel synthesis."""
import json
import logging
from typing import Optional
from config import PROMPTS_DIR, OPERATIVE_CODENAMES
from agents.mistral_client import chat_completion, chat_completion_json
from game.state_manager import load_world_state
from game.operative_manager import load_operative, get_operative_public_info

logger = logging.getLogger(__name__)


def _load_orchestrator_template() -> str:
    """Load the orchestrator system prompt template."""
    path = PROMPTS_DIR / "orchestrator.md"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _build_orchestrator_prompt() -> str:
    """Build the orchestrator system prompt with current world state injected."""
    template = _load_orchestrator_template()
    world_state = load_world_state()
    
    # Format world state (sanitized — no loyalty scores)
    world_state_text = json.dumps({
        "turn": world_state["turn"],
        "regions": world_state["regions"],
        "threat_level": world_state["threat_level"],
        "agency_exposure_level": world_state["agency_exposure_level"],
        "director_trust_score": world_state["director_trust_score"],
        "compromised_assets": world_state["compromised_assets"],
    }, indent=2)
    
    # Format mission log (last 10 entries)
    recent_missions = world_state.get("mission_log", [])[-10:]
    if recent_missions:
        mission_log_text = json.dumps(recent_missions, indent=2)
    else:
        mission_log_text = "No missions completed yet."
    
    # Format operative list (public info only)
    operative_list = []
    for codename in OPERATIVE_CODENAMES:
        try:
            op = load_operative(codename)
            operative_list.append(
                f"- {codename}: Located in {op['location']}, Status: {op['current_status']}"
            )
        except Exception:
            operative_list.append(f"- {codename}: Status unknown")
    operative_list_text = "\n".join(operative_list)
    
    # Inject into template
    prompt = template.replace("{world_state}", world_state_text)
    prompt = prompt.replace("{mission_log}", mission_log_text)
    prompt = prompt.replace("{operative_list}", operative_list_text)
    
    return prompt


async def generate_world_event() -> dict:
    """Generate a world event based on current state.
    
    Returns:
        Dict with event_title, event_description, affected_region, 
        tension_impact, suggested_actions.
    """
    system_prompt = _build_orchestrator_prompt()
    user_message = "MODE: GENERATE_EVENT\n\nGenerate a new geopolitical world event based on current tensions and missions."
    
    try:
        response = await chat_completion_json(system_prompt, user_message)
        event = json.loads(response)
        logger.info(f"World event generated: {event.get('event_title', 'Unknown')}")
        return event
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Failed to parse world event: {e}")
        # Fallback event
        return {
            "event_title": "Intelligence Intercept Detected",
            "event_description": "Signals intelligence has detected unusual communications activity across multiple monitored frequencies. The pattern suggests coordinated movement by an unknown entity. Analysis is ongoing, but the Director should be prepared for rapid developments.",
            "affected_region": "middle_east",
            "tension_impact": 5,
            "suggested_actions": [
                "Task an operative to investigate the signal source",
                "Increase monitoring on all channels",
                "Brief all operatives on heightened alert status"
            ]
        }


async def route_order(director_order: str) -> dict:
    """Parse a director's order and route it to the correct operative.
    
    Args:
        director_order: The raw text order from the Director.
    
    Returns:
        Dict with target_operative, mission_brief, mission_type, risk_level.
    """
    system_prompt = _build_orchestrator_prompt()
    user_message = (
        f"MODE: ROUTE_ORDER\n\n"
        f"The Director has issued the following order:\n\"{director_order}\"\n\n"
        f"Parse this order, identify the correct target operative, and format a mission brief."
    )
    
    try:
        response = await chat_completion_json(system_prompt, user_message)
        routing = json.loads(response)
        
        # Validate target operative
        target = routing.get("target_operative", "").upper()
        if target not in OPERATIVE_CODENAMES:
            # Try to extract codename from the order text
            for codename in OPERATIVE_CODENAMES:
                if codename in director_order.upper():
                    target = codename
                    break
            else:
                target = OPERATIVE_CODENAMES[0]  # Default fallback
            routing["target_operative"] = target
        
        logger.info(f"Order routed to {target}: {routing.get('mission_type', 'unknown')}")
        return routing
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Failed to parse order routing: {e}")
        # Fallback: try to detect operative name in order
        target = OPERATIVE_CODENAMES[0]
        for codename in OPERATIVE_CODENAMES:
            if codename in director_order.upper():
                target = codename
                break
        
        return {
            "target_operative": target,
            "mission_brief": director_order,
            "mission_type": "reconnaissance",
            "risk_level": "medium",
        }


async def synthesize_intel(operative_reports: list) -> str:
    """Synthesize operative reports into a coherent intelligence briefing.
    
    Args:
        operative_reports: List of dicts with codename and response text.
    
    Returns:
        Narrative intelligence briefing string.
    """
    system_prompt = _build_orchestrator_prompt()
    
    reports_text = "\n\n".join([
        f"=== REPORT FROM {r['codename']} ===\n{r['response']}"
        for r in operative_reports
    ])
    
    user_message = (
        f"MODE: SYNTHESIZE_INTEL\n\n"
        f"The following operative reports have been received:\n\n{reports_text}\n\n"
        f"Synthesize these into a coherent intelligence briefing for the Director."
    )
    
    try:
        briefing = await chat_completion(system_prompt, user_message)
        logger.info("Intel synthesis completed")
        return briefing
    except Exception as e:
        logger.error(f"Intel synthesis failed: {e}")
        return "INTELLIGENCE BRIEFING UNAVAILABLE — Communications disruption detected. Awaiting signal restoration."


async def generate_turn_briefing() -> str:
    """Generate a turn-start briefing for the Director.
    
    Returns:
        Narrative briefing string summarizing current situation.
    """
    system_prompt = _build_orchestrator_prompt()
    user_message = (
        "MODE: TURN_BRIEFING\n\n"
        "Generate a comprehensive situation briefing for the Director at the start of this turn. "
        "Include threat assessment, regional summaries, operative status overview, and recommended priorities."
    )
    
    try:
        briefing = await chat_completion(system_prompt, user_message)
        logger.info("Turn briefing generated")
        return briefing
    except Exception as e:
        logger.error(f"Turn briefing generation failed: {e}")
        return "SITUATION BRIEFING UNAVAILABLE — Secure channel interference detected. Manual assessment recommended."
