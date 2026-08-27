import logging
from typing import Dict, List, Any, Callable, Optional
from google.adk import Agent, Context, Event, Workflow, Runner
from src.core.config import settings

logger = logging.getLogger("studiosonar.adk")

def create_adk_agent(
    name: str,
    instruction: str,
    tools: Optional[List[Callable]] = None,
    model: Optional[str] = None
) -> Agent:
    """
    Factory function to instantiate a native Google ADK Agent (v2.7.1).
    Binds declarative tools and Vertex AI / Gemini Flash instruction schema directly.
    """
    active_model = model or settings.gemini_model or "gemini-2.5-flash"
    return Agent(
        name=name,
        model=active_model,
        instruction=instruction,
        tools=tools or []
    )

class ADKAgentMessage:
    """
    Structured Agent Event/Handoff envelope aligned with ADK Event contracts.
    """
    def __init__(self, sender: str, recipient: str, message_type: str, content: Dict[str, Any]):
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
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
    Standard Base Wrapper around Native Google ADK Agent (v2.7.1).
    Provides native tool binding, lifecycle execution, and event tracing.
    """

    def __init__(
        self,
        name: str,
        role: str,
        system_instruction: str,
        tools: Optional[List[Callable]] = None,
        model: Optional[str] = None
    ):
        self.name = name
        self.role = role
        self.system_instruction = system_instruction
        self.tools_list = tools or []
        self.tools = {tool.__name__: tool for tool in self.tools_list}
        self.message_log: List[ADKAgentMessage] = []
        self.model = model or settings.gemini_model or "gemini-2.5-flash"
        
        # Native Google ADK Agent instance
        self.adk_agent: Agent = create_adk_agent(
            name=self.name,
            instruction=f"{self.role}. {self.system_instruction}",
            tools=self.tools_list,
            model=self.model
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

    def as_native_agent(self) -> Agent:
        """Returns the pure native Google ADK Agent instance."""
        return self.adk_agent
