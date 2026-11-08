"""
AgentCut MCP: Pydantic Data Contracts & Request/Response Models
Spec reference: docs/specs/mcp-server/spec.md
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ProjectCreateRequest(BaseModel):
    name: str = Field(..., description="Project human-readable title")
    width: int = Field(1920, description="Video width in pixels (e.g. 1920 for 16:9, 1080 for 9:16)")
    height: int = Field(1080, description="Video height in pixels (e.g. 1080 for 16:9, 1920 for 9:16)")
    fps: float = Field(30.0, description="Project timeline framerate")

class MediaIngestRequest(BaseModel):
    project_id: str = Field(..., description="Target project ID")
    file_path: str = Field(..., description="Path to source media file")
    asset_id: Optional[str] = Field(None, description="Custom asset ID (auto-generated if omitted)")

class ClipAddRequest(BaseModel):
    project_id: str = Field(..., description="Project ID")
    track_index: int = Field(1, description="Track index (1=V1, 2=V2, etc.)")
    clip_id: str = Field(..., description="Unique ID for this clip on the timeline")
    asset_id: str = Field(..., description="Source media asset ID")
    asset_path: str = Field(..., description="Path to source media file")
    timeline_in: float = Field(..., description="Timeline start position in seconds")
    timeline_out: float = Field(..., description="Timeline end position in seconds")
    source_in: float = Field(0.0, description="Source footage in-point in seconds")
    source_out: float = Field(..., description="Source footage out-point in seconds")
    scale: float = Field(1.0, description="Scale factor (e.g. 1.15 for punch-in)")

class ClipSplitRequest(BaseModel):
    project_id: str = Field(..., description="Project ID")
    clip_id: str = Field(..., description="ID of clip to slice")
    split_at: float = Field(..., description="Master timeline timestamp where the slice occurs")

class ClipTrimRequest(BaseModel):
    project_id: str = Field(..., description="Project ID")
    clip_id: str = Field(..., description="ID of clip to trim")
    delta_in: float = Field(0.0, description="Seconds to adjust start point (+ expands, - trims)")
    delta_out: float = Field(0.0, description="Seconds to adjust end point")

class ClipMoveRequest(BaseModel):
    project_id: str = Field(..., description="Project ID")
    clip_id: str = Field(..., description="ID of clip to move")
    new_timeline_in: float = Field(..., description="New starting position on timeline")
    new_track_index: Optional[int] = Field(None, description="Optional target track index")

class PunchInRequest(BaseModel):
    project_id: str = Field(..., description="Project ID")
    clip_id: str = Field(..., description="ID of clip to punch-in")
    scale: float = Field(1.15, description="Zoom scale factor (default 1.15x for jump cut masking)")

class CaptionAddRequest(BaseModel):
    project_id: str = Field(..., description="Project ID")
    caption_id: str = Field(..., description="Unique caption identifier")
    text: str = Field(..., description="Caption text string")
    timeline_in: float = Field(..., description="Start timestamp on timeline")
    timeline_out: float = Field(..., description="End timestamp on timeline")
    font_size: int = Field(36, description="Font point size")
    font_color: str = Field("#FED330", description="Hex color for default text")
    highlight_color: str = Field("#00D9FF", description="Hex color for active highlighted word")

class TransitionAddRequest(BaseModel):
    project_id: str = Field(..., description="Project ID")
    clip_id: str = Field(..., description="Clip receiving the transition")
    transition_type: str = Field("crossfade", description="Transition type: crossfade, wipe, dip_to_black")
    duration: float = Field(0.5, description="Transition duration in seconds")

class RenderDispatchRequest(BaseModel):
    project_id: str = Field(..., description="Project ID")
    output_path: str = Field(..., description="Output MP4 file path")
    export_kdenlive: bool = Field(True, description="Whether to also export native .kdenlive project file")

class LockAcquireRequest(BaseModel):
    project_id: str = Field(..., description="Project ID")
    track_id: str = Field(..., description="Track identifier (e.g. track_video_1)")
    start_time: float = Field(..., description="Interval start in seconds")
    end_time: float = Field(..., description="Interval end in seconds")
    agent_id: str = Field(..., description="Agent acquiring the lock")
    lease_seconds: float = Field(15.0, description="Lock expiration duration")

class LockReleaseRequest(BaseModel):
    project_id: str = Field(..., description="Project ID")
    track_id: str = Field(..., description="Track identifier")
    agent_id: str = Field(..., description="Agent releasing the lock")

class EventLogRequest(BaseModel):
    project_id: str = Field(..., description="Project ID")
    agent_id: str = Field(..., description="Agent ID")
    agent_name: str = Field(..., description="Agent human-readable name")
    agent_role: str = Field(..., description="Role: director, analyst, editor, audio, captions, colorist, qc")
    agent_color: str = Field(..., description="Agent visual branding hex color")
    action_type: str = Field(..., description="Action verb (media_drag_drop, clip_split, punch_in_apply, etc.)")
    description: str = Field(..., description="Human-readable decision explanation")
    target_track_index: int = Field(1, description="Target timeline track index")
    timeline_time_in: float = Field(0.0, description="Timeline timestamp where action occurs")
    duration: float = Field(0.0, description="Duration affected by the action")
    start_coords: Optional[Dict[str, int]] = Field(None, description="Cursor starting pixel coords {x, y}")
    target_coords: Optional[Dict[str, int]] = Field(None, description="Cursor target pixel coords {x, y}")
    cursor_tool_icon: str = Field("pointer", description="Icon style: pointer, grab, razor, text_stamp")
    haptic_visual: str = Field("none", description="Visual effect: ripple, slice_particle, glow_pulse, snap_shadow")

