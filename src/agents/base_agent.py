import json
import logging
from typing import Dict, List, Any, Callable, Optional
from google.adk import Agent, Context, Event, Workflow, Runner
from src.core.config import settings

logger = logging.getLogger("studiosonar.adk")

class ADKAgentMessage:
    """Standardized inter-agent communication message contract in Google ADK."""
    def __init__(self, sender: str, recipient: str, message_type: str, content: Dict[str, Any]):
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type # e.g. "ANOMALY_HANDOFF", "STRATEGY_REQUEST", "TASK_COMPLETED"
        self.content = content

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type,
            "content": self.content
        }

class BaseADKAgent:
    """
    Base class for Google ADK Agents powered by google-adk (v2.7.1).
    Provides native tool execution, agent context memory, and inter-agent A2A messaging.
    """

    def __init__(
        self,
        name: str,
        role: str,
        system_instruction: str,
        tools: Optional[List[Callable]] = None
    ):
        self.name = name
        self.role = role
        self.system_instruction = system_instruction
        self.tools = {tool.__name__: tool for tool in (tools or [])}
        self.message_log: List[ADKAgentMessage] = []
        
        # Native Google ADK Agent instance
        self._adk_agent = Agent(
            name=name,
            description=f"{role}: {system_instruction[:100]}",
            tools=tools or []
        )

    def log_message(self, msg: ADKAgentMessage):
        self.message_log.append(msg)
        logger.info(f"[{msg.sender} ➔ {msg.recipient}] ({msg.message_type}): {list(msg.content.keys())}")

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Executes a registered MCP tool within this agent's domain."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not registered in {self.name}")
        tool_fn = self.tools[tool_name]
        return tool_fn(**kwargs)
