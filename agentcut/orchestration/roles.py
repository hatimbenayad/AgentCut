"""
AgentCut Orchestration: Specialized Agent Roles & Personas
Spec reference: docs/specs/agent-orchestration/spec.md
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from agentcut.core.events import AgentVisualIdentity

@dataclass
class AgentRoleConfig:
    role: str
    name: str
    color: str
    allowed_tracks: List[str]
    description: str

AGENT_ROLES: Dict[str, AgentRoleConfig] = {
    "director": AgentRoleConfig(
        role="director",
        name="Director",
        color="#E056FD",
        allowed_tracks=["all"],
        description="Decomposes human creative prompts into narrative edit plans and manages agent workflow"
    ),
    "analyst": AgentRoleConfig(
        role="analyst",
        name="Footage Analyst",
        color="#F0932B",
        allowed_tracks=[],
        description="Inspects multimodal video intelligence graphs to identify hooks, topics, pauses, and OCR"
    ),
    "editor": AgentRoleConfig(
        role="editor",
        name="Video Editor",
        color="#00D9FF",
        allowed_tracks=["video"],
        description="Assembles primary video tracks, performs cuts, jump cuts, punch-ins, and pacing trims"
    ),
    "audio": AgentRoleConfig(
        role="audio",
        name="Audio Engineer",
        color="#686DE0",
        allowed_tracks=["audio"],
        description="Balances audio levels, normalizes dialogue loudness (-14 LUFS), and ducks background music"
    ),
    "captions": AgentRoleConfig(
        role="captions",
        name="Caption Designer",
        color="#F9CA24",
        allowed_tracks=["subtitle"],
        description="Generates animated, word-level synchronized typography overlays"
    ),
    "colorist": AgentRoleConfig(
        role="colorist",
        name="Colorist",
        color="#6AB04C",
        allowed_tracks=["video"],
        description="Applies cinematic color grading, exposure balance, and contrast curve adjustments"
    ),
    "qc": AgentRoleConfig(
        role="qc",
        name="Quality Controller",
        color="#EB4D4B",
        allowed_tracks=["all"],
        description="Performs automated verification: black gaps, flash frames, speech clipping, and caption collisions"
    )
}

class BaseAgent:
    """Base class for specialized autonomous editing agents."""

    def __init__(self, agent_id: str, role_key: str):
        self.config = AGENT_ROLES[role_key]
        self.agent_id = agent_id
        self.visual_identity = AgentVisualIdentity(
            agent_id=self.agent_id,
            name=self.config.name,
            role=self.config.role,
            color=self.config.color
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.config.role,
            "name": self.config.name,
            "color": self.config.color,
            "description": self.config.description
        }

