"""Turn Manager — orchestrates the full turn cycle."""
import logging
import uuid
from datetime import datetime
from typing import Optional

from game.state_manager import (
    load_world_state, save_world_state, advance_turn,
    add_world_event, is_game_over, update_region_tension
)
from game.operative_manager import load_all_operatives
from game.decision_engine import process_operative_response, process_event_response
from agents.orchestrator import (
    generate_world_event, route_order, synthesize_intel, generate_turn_briefing
)
from agents.operative import call_operative

logger = logging.getLogger(__name__)


class TurnManager:
    """Manages the game turn cycle."""
    
    def __init__(self):
        self.current_event: Optional[dict] = None
        self.transmissions: list = []
        self.current_briefing: str = ""
        self.rogue_events: list = []
    
    async def start_turn(self) -> dict:
        """Start a new turn: generate world event + briefing.
        
        Returns:
            Dict with event, briefing, game_over status.
        """
        state = load_world_state()
        
        # Check game over
        game_over = is_game_over(state)
        if game_over:
            return {"game_over": game_over}
        
        # Generate world event
        event = await generate_world_event()
        event["turn"] = state["turn"]
        event["timestamp"] = datetime.now().isoformat()
        
        # Apply tension impact from event
        affected_region = event.get("affected_region")
        tension_impact = event.get("tension_impact", 0)
        if affected_region and tension_impact:
            state = load_world_state()
            update_region_tension(state, affected_region, tension_impact)
            save_world_state(state)
        
        # Store event in world state
        state = load_world_state()
        add_world_event(state, event)
        state["world_events"] = state.get("world_events", [])[-20:]  # Keep last 20
        save_world_state(state)
        
        self.current_event = event
        
        # Generate briefing
        briefing = await generate_turn_briefing()
        self.current_briefing = briefing
        
        return {
            "turn": state["turn"],
            "event": event,
            "briefing": briefing,
            "game_over": None,
        }
    
    async def issue_order(self, director_order: str) -> dict:
        """Director issues an order — routed through orchestrator to operative.
        
        Args:
            director_order: Raw text order from the Director.
        
        Returns:
            Dict with routing info, operative response, and state changes.
        """
        state = load_world_state()
        
        # Check game over
        game_over = is_game_over(state)
        if game_over:
            return {"game_over": game_over}
        
        # Route order through orchestrator
        routing = await route_order(director_order)
        target = routing["target_operative"]
        mission_brief = routing.get("mission_brief", director_order)
        
        # Call operative agent
        response_data = await call_operative(target, mission_brief)
        
        # Process response — update state
        changes = process_operative_response(target, director_order, response_data)
        
        # Create transmission record
        transmission = {
            "id": str(uuid.uuid4()),
            "turn": state["turn"],
            "timestamp": datetime.now().isoformat(),
            "codename": target,
            "order": director_order,
            "response": response_data["response"],
            "mission_type": routing.get("mission_type", "unknown"),
            "risk_level": routing.get("risk_level", "unknown"),
        }
        self.transmissions.append(transmission)
        
        # Synthesize intel
        intel_report = await synthesize_intel([{
            "codename": target,
            "response": response_data["response"],
        }])
        
        return {
            "transmission": transmission,
            "routing": routing,
            "intel_report": intel_report,
            "changes": changes,
            "game_over": is_game_over(load_world_state()),
        }
    
    async def respond_to_event(self, action: str) -> dict:
        """Director responds to the current world event.
        
        Args:
            action: The action text chosen by the Director.
        
        Returns:
            Dict with action result.
        """
        if not self.current_event:
            return {"error": "No active event to respond to"}
        
        result = process_event_response(action, self.current_event)
        return result
    
    async def end_turn(self) -> dict:
        """End the current turn — advance state, check triggers.
        
        Returns:
            Dict with new turn number, any rogue events, game_over status.
        """
        state = load_world_state()
        
        # Import here to avoid circular imports
        from game.rogue_engine import check_autonomous_triggers
        
        # Check autonomous triggers
        rogue_events = await check_autonomous_triggers()
        self.rogue_events = rogue_events
        
        # Advance turn
        state = load_world_state()  # Reload after rogue events may have modified state
        advance_turn(state)
        save_world_state(state)
        
        return {
            "new_turn": state["turn"],
            "threat_level": state["threat_level"],
            "rogue_events": rogue_events,
            "game_over": is_game_over(state),
        }
    
    def get_transmissions(self) -> list:
        """Get all transmissions from the current game."""
        return self.transmissions
    
    def get_current_briefing(self) -> str:
        """Get the current turn's briefing."""
        return self.current_briefing
    
    def get_rogue_events(self) -> list:
        """Get rogue events from the last turn."""
        return self.rogue_events


# Global turn manager instance
turn_manager = TurnManager()
