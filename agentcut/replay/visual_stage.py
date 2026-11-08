"""
AgentCut Replay: Visual Stage Keyframe Synthesizer
Spec reference: docs/specs/activity-replay/spec.md
ADR reference: docs/architecture/architecture-decisions.md (ADR-006)
"""

from typing import List, Dict, Any, Optional
from agentcut.core.events import EditingEvent

class VisualStageSynthesizer:
    """Translates discrete SQLite editing events into continuous 60 FPS multi-cursor animation states."""

    @staticmethod
    def synthesize_keyframes(
        events: List[EditingEvent],
        fps: int = 60,
        speed_multiplier: float = 1.0
    ) -> Dict[str, Any]:
        if not events:
            return {"total_duration_sec": 0.0, "frames": [], "agents": []}

        # Identify unique agents
        agents_map: Dict[str, Dict[str, Any]] = {}
        for evt in events:
            if evt.agent.agent_id not in agents_map:
                agents_map[evt.agent.agent_id] = {
                    "agent_id": evt.agent.agent_id,
                    "name": evt.agent.name,
                    "role": evt.agent.role,
                    "color": evt.agent.color
                }

        # Normalize wall-clock time so replay starts at t=0
        first_time = events[0].wall_clock_time
        normalized_events = []
        for evt in events:
            offset = max(0.0, (evt.wall_clock_time - first_time) / speed_multiplier)
            normalized_events.append({
                "event": evt,
                "replay_start_time": offset,
                "replay_duration_sec": (evt.visual_staging.duration_ms / 1000.0) / speed_multiplier
            })

        total_duration = max(e["replay_start_time"] + e["replay_duration_sec"] for e in normalized_events) + 1.0
        total_frames = int(total_duration * fps)

        # Precompute per-frame cursor positions and timeline states
        timeline_clips: List[Dict[str, Any]] = []
        frames: List[Dict[str, Any]] = []

        for frame_idx in range(total_frames):
            current_time = frame_idx / float(fps)
            active_cursors: List[Dict[str, Any]] = []
            active_haptics: List[Dict[str, Any]] = []

            for ne in normalized_events:
                evt: EditingEvent = ne["event"]
                t0 = ne["replay_start_time"]
                t1 = t0 + ne["replay_duration_sec"]

                if t0 <= current_time <= t1:
                    # Calculate progression [0.0, 1.0]
                    progress = (current_time - t0) / max(0.001, ne["replay_duration_sec"])
                    # Apply smooth ease-in-out easing
                    eased = 0.5 - 0.5 * (1 - 2 * progress) if progress < 0.5 else 0.5 + 0.5 * (2 * progress - 1)
                    
                    # Interpolate (x, y)
                    x0 = evt.visual_staging.start_coords["x"]
                    y0 = evt.visual_staging.start_coords["y"]
                    x1 = evt.visual_staging.target_coords["x"]
                    y1 = evt.visual_staging.target_coords["y"]

                    cx = x0 + (x1 - x0) * eased
                    cy = y0 + (y1 - y0) * eased

                    active_cursors.append({
                        "agent_id": evt.agent.agent_id,
                        "agent_name": evt.agent.name,
                        "color": evt.agent.color,
                        "role": evt.agent.role,
                        "x": round(cx, 1),
                        "y": round(cy, 1),
                        "tool": evt.visual_staging.cursor_tool_icon,
                        "action_label": evt.description
                    })

                    # Trigger haptic pulse at drop moment
                    if progress > 0.85 and evt.visual_staging.haptic_visual != "none":
                        active_haptics.append({
                            "type": evt.visual_staging.haptic_visual,
                            "x": round(x1, 1),
                            "y": round(y1, 1),
                            "color": evt.agent.color
                        })

            frames.append({
                "frame": frame_idx,
                "timestamp_sec": round(current_time, 3),
                "cursors": active_cursors,
                "haptics": active_haptics
            })

        return {
            "total_duration_sec": round(total_duration, 2),
            "total_frames": total_frames,
            "fps": fps,
            "speed_multiplier": speed_multiplier,
            "agents": list(agents_map.values()),
            "frames": frames
        }
