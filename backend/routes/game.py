"""Game API routes — all game-related endpoints."""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from game.state_manager import load_world_state, get_public_world_state, is_game_over
from game.operative_manager import get_all_operatives_public, get_operative_public_info
from game.turn_manager import turn_manager
from game.decision_engine import handle_extraction_order
from utils.create_backups import reset_game_state

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["game"])


class OrderRequest(BaseModel):
    order: str
    operative: Optional[str] = None


class EventResponseRequest(BaseModel):
    action: str


class ExtractRequest(BaseModel):
    codename: str


# --- World State ---

@router.get("/world-state")
async def get_world_state():
    """Returns current world state (public view — no loyalty scores)."""
    try:
        state = load_world_state()
        return get_public_world_state(state)
    except Exception as e:
        logger.error(f"Error loading world state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Operatives ---

@router.get("/operatives")
async def get_operatives():
    """Returns operative list with public info (codename, location, signal quality)."""
    try:
        return get_all_operatives_public()
    except Exception as e:
        logger.error(f"Error loading operatives: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/operatives/{codename}")
async def get_operative(codename: str):
    """Returns public info for a specific operative."""
    try:
        return get_operative_public_info(codename.upper())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Operative {codename} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Orders ---

@router.post("/order")
async def issue_order(request: OrderRequest):
    """Director issues an order to an operative.
    
    Routes through orchestrator → operative → state updates.
    """
    try:
        # If operative specified, prepend to order for routing
        order_text = request.order
        if request.operative:
            order_text = f"{request.operative}: {order_text}"
        
        result = await turn_manager.issue_order(order_text)
        
        if result.get("game_over"):
            return result
        
        return result
    except Exception as e:
        logger.error(f"Error processing order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Turn Management ---

@router.post("/start-turn")
async def start_turn():
    """Start a new turn — generates world event and briefing."""
    try:
        result = await turn_manager.start_turn()
        return result
    except Exception as e:
        logger.error(f"Error starting turn: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/end-turn")
async def end_turn():
    """End the current turn — triggers autonomous events, advances state."""
    try:
        result = await turn_manager.end_turn()
        return result
    except Exception as e:
        logger.error(f"Error ending turn: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/respond-to-event")
async def respond_to_event(request: EventResponseRequest):
    """Director responds to a world event."""
    try:
        result = await turn_manager.respond_to_event(request.action)
        return result
    except Exception as e:
        logger.error(f"Error responding to event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Transmissions ---

@router.get("/transmissions")
async def get_transmissions():
    """Returns all transmission log entries."""
    return turn_manager.get_transmissions()


# --- Briefing ---

@router.get("/briefing")
async def get_briefing():
    """Returns current turn's intelligence briefing."""
    return {"briefing": turn_manager.get_current_briefing()}


# --- Rogue Events ---

@router.get("/rogue-events")
async def get_rogue_events():
    """Returns rogue events from the last turn."""
    return turn_manager.get_rogue_events()


# --- Extraction ---

@router.post("/extract")
async def extract_operative(request: ExtractRequest):
    """Director orders extraction of an operative."""
    try:
        result = handle_extraction_order(request.codename.upper())
        return result
    except Exception as e:
        logger.error(f"Error extracting operative: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Game Management ---

@router.post("/new-game")
async def new_game():
    """Reset all game state to initial values and start fresh."""
    try:
        reset_game_state()
        # Reset turn manager
        turn_manager.current_event = None
        turn_manager.transmissions = []
        turn_manager.current_briefing = ""
        turn_manager.rogue_events = []
        
        return {"message": "Game reset to initial state", "turn": 1}
    except Exception as e:
        logger.error(f"Error resetting game: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/game-over")
async def check_game_over():
    """Check if any game-over condition is met."""
    state = load_world_state()
    result = is_game_over(state)
    if result:
        return result
    return {"game_over": False}
