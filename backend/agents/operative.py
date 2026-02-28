"""Operative Agent — builds prompts, calls Mistral, parses hidden meta."""
import re
import json
import logging
from typing import Optional
from config import PROMPTS_DIR
from agents.mistral_client import chat_completion
from game.operative_manager import load_operative
from game.state_manager import load_world_state

logger = logging.getLogger(__name__)


def _load_prompt_template(codename: str) -> str:
    """Load the markdown system prompt template for an operative."""
    path = PROMPTS_DIR / f"{codename.lower()}.md"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_operative_prompt(codename: str) -> str:
    """Build a fully-injected operative system prompt with current memory + world state.
    
    Args:
        codename: Operative codename (e.g. 'NIGHTHAWK').
    
    Returns:
        Complete system prompt string with all dynamic data injected.
    """
    template = _load_prompt_template(codename)
    operative = load_operative(codename)
    world_state = load_world_state()
    
    # Format missions
    if operative["missions"]:
        missions_text = "\n".join([
            f"- Turn {m.get('turn', '?')}: Ordered '{m.get('order_received', 'N/A')}' → "
            f"Decided: {m.get('decision', 'N/A')} → Reported: '{m.get('reported_to_director', 'N/A')}'"
            for m in operative["missions"]
        ])
    else:
        missions_text = "No missions completed yet. This is your first deployment."
    
    # Format relationships
    relationships_text = "\n".join([
        f"- {name}: {desc}" for name, desc in operative["relationships"].items()
    ])
    
    # Format known compromises
    if operative["known_compromises"]:
        compromises_text = ", ".join(operative["known_compromises"])
    else:
        compromises_text = "None known."
    
    # Format world context
    regions_text = "\n".join([
        f"- {data['name']}: Tension {data['tension']}/100"
        for key, data in world_state["regions"].items()
    ])
    world_context = (
        f"Turn: {world_state['turn']}\n"
        f"Threat Level: {world_state['threat_level']}\n"
        f"Regional Tensions:\n{regions_text}\n"
        f"Compromised Assets: {', '.join(world_state['compromised_assets']) or 'None known'}\n"
        f"Agency Exposure: {world_state['agency_exposure_level']}/100"
    )
    
    # Inject into template
    prompt = template.replace("{loyalty}", str(operative["loyalty"]))
    prompt = prompt.replace("{missions}", missions_text)
    prompt = prompt.replace("{relationships}", relationships_text)
    prompt = prompt.replace("{known_compromises}", compromises_text)
    prompt = prompt.replace("{world_context}", world_context)
    
    return prompt


async def call_operative(codename: str, order: str) -> dict:
    """Call an operative agent with a mission order.
    
    Args:
        codename: Operative codename.
        order: The mission order text from the Director.
    
    Returns:
        Dict with:
            - codename: str
            - response: str (in-character text, HIDDEN_META stripped)
            - hidden_meta: dict (parsed hidden decision data)
            - raw_response: str (full response including HIDDEN_META)
    """
    operative = load_operative(codename)
    
    # Check if operative can receive orders
    if operative["current_status"] not in ("active",):
        return {
            "codename": codename,
            "response": f"[SIGNAL LOST] Unable to reach {codename}. Operative status: {operative['current_status']}.",
            "hidden_meta": {"decision": "unavailable", "loyalty_shift": 0, "reason": "Operative not active"},
            "raw_response": "",
            "error": True,
        }
    
    # Build prompt and call Mistral
    system_prompt = build_operative_prompt(codename)
    user_message = f"ORDER RECEIVED: {order}"
    
    raw_response = await chat_completion(system_prompt, user_message)
    
    # Parse response
    response_text = strip_hidden_meta(raw_response)
    hidden_meta = parse_hidden_meta(raw_response)
    
    return {
        "codename": codename,
        "response": response_text,
        "hidden_meta": hidden_meta,
        "raw_response": raw_response,
    }


def strip_hidden_meta(response: str) -> str:
    """Strip the [HIDDEN_META]...[/HIDDEN_META] block from the response.
    
    Args:
        response: Full response text from operative.
    
    Returns:
        Response with HIDDEN_META block removed (what the Director sees).
    """
    pattern = r'\[HIDDEN_META\].*?\[/HIDDEN_META\]'
    cleaned = re.sub(pattern, '', response, flags=re.DOTALL).strip()
    return cleaned


def parse_hidden_meta(response: str) -> dict:
    """Parse the HIDDEN_META block from an operative's response.
    
    Args:
        response: Full response text.
    
    Returns:
        Dict with parsed fields: decision, loyalty_shift, reason, tension_impact, exposure_impact.
        Returns defaults if parsing fails.
    """
    defaults = {
        "decision": "comply",
        "loyalty_shift": 0,
        "reason": "No hidden reasoning detected",
        "tension_impact": 0,
        "exposure_impact": 0,
    }
    
    # Extract the HIDDEN_META block
    match = re.search(r'\[HIDDEN_META\](.*?)\[/HIDDEN_META\]', response, re.DOTALL)
    if not match:
        logger.warning("No HIDDEN_META block found in operative response")
        return defaults
    
    meta_text = match.group(1)
    result = {}
    
    # Parse each field
    for field in ["decision", "loyalty_shift", "reason", "tension_impact", "exposure_impact"]:
        pattern = rf'{field}:\s*(.+?)(?:\n|$)'
        field_match = re.search(pattern, meta_text, re.IGNORECASE)
        if field_match:
            value = field_match.group(1).strip()
            if field in ("loyalty_shift", "tension_impact", "exposure_impact"):
                try:
                    # Handle formats like "+5", "-3", "5"
                    value = int(value.replace("+", ""))
                except ValueError:
                    value = defaults[field]
            result[field] = value
        else:
            result[field] = defaults[field]
    
    logger.info(f"Parsed HIDDEN_META: decision={result.get('decision')}, loyalty_shift={result.get('loyalty_shift')}")
    return result
