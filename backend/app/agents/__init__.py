"""
MileSync Multi-Agent System

This package contains the 6-layer agent architecture:
- Foundation Agent: Goal intake & user profiling
- Planning Agent: SMART conversion & task breakdown
- Execution Agent: Task management & progress tracking
- Sustainability Agent: Habit formation & pattern detection
- Support Agent: Resource curation & recommendations
- Psychological Agent: Motivation & mindset coaching

All agents are orchestrated by the AgentCoordinator.
"""

from app.agents.base_agent import BaseAgent, AgentType, AgentContext, AgentResponse
from app.agents.coordinator import AgentCoordinator

__all__ = [
    "BaseAgent",
    "AgentType",
    "AgentContext", 
    "AgentResponse",
    "AgentCoordinator",
]
