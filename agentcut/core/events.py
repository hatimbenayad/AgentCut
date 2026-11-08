"""
AgentCut Core: Replay Event Models & Data Contracts
Spec reference: docs/specs/activity-replay/event-schema.md
ADR reference: docs/architecture/architecture-decisions.md (ADR-006, ADR-009)
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
import time
import uuid

@dataclass
class AgentVisualIdentity:
    agent_id: str
    name: str
    role: str                       # 'director', 'analyst', 'editor', 'audio', 'captions', 'colorist', 'qc'
    color: str                      # '#00D9FF' for editor, '#FED330' for captions, etc.

@dataclass
class VisualStaging:
    start_coords: Dict[str, float]  # {'x': 100, 'y': 200}
    target_coords: Dict[str, float] # {'x': 450, 'y': 620}
    motion_curve: str = "ease_in_out"
    duration_ms: float = 600.0
    cursor_tool_icon: str = "pointer" # 'pointer', 'razor', 'grab', 'text_stamp', 'fader'
    haptic_visual: str = "none"      # 'none', 'slice_particle', 'glow_pulse', 'ripple'

@dataclass
class EditingEvent:
    event_id: str
    project_id: str
    sequence_number: int
    agent: AgentVisualIdentity
    action_type: str                # 'media_drag_drop', 'clip_split', 'clip_trim', 'caption_stamp', etc.
    description: str
    target_track_index: int
    timeline_time_in: float
    duration: float = 0.0
    source_asset_id: Optional[str] = None
    source_range: Optional[List[float]] = None
    visual_staging: VisualStaging = field(default_factory=lambda: VisualStaging({'x':0,'y':0}, {'x':0,'y':0}))
    wall_clock_time: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def create(
        cls,
        project_id: str,
        sequence_number: int,
        agent_id: str,
        agent_name: str,
        agent_role: str,
        agent_color: str,
        action_type: str,
        description: str,
        target_track_index: int,
        timeline_time_in: float,
        duration: float = 0.0,
        source_asset_id: Optional[str] = None,
        source_range: Optional[List[float]] = None,
        start_coords: Optional[Dict[str, float]] = None,
        target_coords: Optional[Dict[str, float]] = None,
        cursor_tool_icon: str = "pointer",
        haptic_visual: str = "none",
        duration_ms: float = 600.0
    ) -> "EditingEvent":
        return cls(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            project_id=project_id,
            sequence_number=sequence_number,
            agent=AgentVisualIdentity(
                agent_id=agent_id,
                name=agent_name,
                role=agent_role,
                color=agent_color
            ),
            action_type=action_type,
            description=description,
            target_track_index=target_track_index,
            timeline_time_in=timeline_time_in,
            duration=duration,
            source_asset_id=source_asset_id,
            source_range=source_range,
            visual_staging=VisualStaging(
                start_coords=start_coords or {"x": 100, "y": 200},
                target_coords=target_coords or {"x": 400, "y": 600},
                cursor_tool_icon=cursor_tool_icon,
                haptic_visual=haptic_visual,
                duration_ms=duration_ms
            )
        )
