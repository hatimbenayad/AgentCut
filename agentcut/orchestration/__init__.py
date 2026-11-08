"""
AgentCut Orchestration: Multi-Agent Production Studio Package
Spec reference: docs/specs/agent-orchestration/spec.md
"""

from agentcut.orchestration.roles import BaseAgent, AGENT_ROLES, AgentRoleConfig
from agentcut.orchestration.coordinator import MultiAgentCoordinator

__all__ = ["BaseAgent", "AGENT_ROLES", "AgentRoleConfig", "MultiAgentCoordinator"]

