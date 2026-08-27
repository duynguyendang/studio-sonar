"""
Google ADK (Agent Development Kit v2.7.1) Core Module.
Provides native Agent factory and Event tracing without custom wrapper abstractions.
"""

import logging
from typing import Dict, List, Any, Callable, Optional
from google.adk import Agent, Workflow, Runner, Context, Event
from src.core.config import settings

logger = logging.getLogger("studiosonar.adk")

def create_pure_adk_agent(
    name: str,
    instruction: str,
    tools: Optional[List[Callable]] = None,
    sub_agents: Optional[List[Agent]] = None,
    model: Optional[str] = None,
    mode: str = "single_turn"
) -> Agent:
    """
    Instantiates a 100% Pure Google ADK Agent (v2.7.1).
    Directly binds tools and LLM instructions without any custom wrapper class.
    Sets mode='single_turn' for native ADK Workflow graph node compatibility.
    """
    active_model = model or settings.gemini_model or "gemini-3.7-flash"
    return Agent(
        name=name,
        model=active_model,
        instruction=instruction,
        tools=tools or [],
        sub_agents=sub_agents or [],
        mode=mode
    )

class ADKEventTracer:
    """Standardized event logging for Google ADK execution lifecycle."""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def record_handoff(self, sender: str, recipient: str, reason: str, payload: Dict[str, Any]):
        event = {
            "sender": sender,
            "recipient": recipient,
            "reason": reason,
            "payload_keys": list(payload.keys())
        }
        self.events.append(event)
        logger.info(f"⚡ [ADK A2A Event] {sender} ➔ {recipient} ({reason})")

    def get_traces(self) -> List[Dict[str, Any]]:
        return self.events

adk_event_tracer = ADKEventTracer()
