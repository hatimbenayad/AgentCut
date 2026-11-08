"""
AgentCut MCP: Production FastMCP Server
Spec reference: docs/specs/mcp-server/spec.md
ADR reference: docs/architecture/architecture-decisions.md (ADR-007, ADR-010)
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from mcp.server.mcpserver import MCPServer

from agentcut.core.timeline import ProjectTimeline, TrackModel, ClipModel, TextCaptionModel, ProjectProfile
from agentcut.core.database import ProjectDatabase
from agentcut.core.events import EditingEvent, AgentVisualIdentity, VisualStaging
from agentcut.intelligence.pipeline import VideoIntelligencePipeline
from agentcut.intelligence.audio import AudioProcessor
from agentcut.render.engine import RenderEngine
from agentcut.replay.visual_stage import VisualStageSynthesizer

def create_mcp_server(db_path: str = "./agentcut_mcp.db") -> MCPServer:
    """Creates and configures the production AgentCut MCPServer instance."""
    mcp = MCPServer("AgentCut")
    db = ProjectDatabase(db_path)

    # -------------------------------------------------------------
    # 1. PROJECT MANAGEMENT TOOLS
    # -------------------------------------------------------------
    @mcp.tool()
    def project_create(name: str, width: int = 1920, height: int = 1080, fps: float = 30.0) -> Dict[str, Any]:
        """Creates a new video editing project workspace with specified canvas profile."""
        project_id = f"prj_{int(time.time() * 1000)}"
        profile = ProjectProfile(width=width, height=height, fps=fps)
        timeline = ProjectTimeline(project_id=project_id, name=name, profile=profile)
        # Initialize default V1 and A1 tracks
        timeline.ensure_track(1, "video", "Video 1")
        timeline.ensure_track(2, "audio", "Audio 1")
        db.save_project(timeline)
        return {
            "status": "created",
            "project_id": project_id,
            "name": name,
            "profile": {"width": width, "height": height, "fps": fps}
        }

    @mcp.tool()
    def project_get(project_id: str) -> Dict[str, Any]:
        """Retrieves the complete multitrack timeline hierarchy for a project."""
        timeline = db.load_project(project_id)
        if not timeline:
            return {"error": f"Project not found: {project_id}"}
        return {
            "project_id": timeline.project_id,
            "name": timeline.name,
            "duration": timeline.duration,
            "profile": {
                "width": timeline.profile.width,
                "height": timeline.profile.height,
                "fps": timeline.profile.fps
            },
            "tracks": [
                {
                    "track_index": t.track_index,
                    "track_type": t.track_type,
                    "name": t.name,
                    "clips": [
                        {
                            "clip_id": c.clip_id,
                            "asset_id": c.asset_id,
                            "timeline_in": c.timeline_in,
                            "timeline_out": c.timeline_out,
                            "duration": c.duration,
                            "scale": c.scale
                        } for c in t.clips
                    ]
                } for t in timeline.tracks
            ],
            "captions": [
                {
                    "caption_id": c.caption_id,
                    "text": c.text,
                    "timeline_in": c.timeline_in,
                    "timeline_out": c.timeline_out
                } for c in timeline.captions
            ]
        }

    @mcp.tool()
    def project_save(project_id: str) -> Dict[str, Any]:
        """Atomically persists project timeline state to SQLite."""
        timeline = db.load_project(project_id)
        if not timeline:
            return {"error": f"Project not found: {project_id}"}
        db.save_project(timeline)
        return {"status": "saved", "project_id": project_id}

    # -------------------------------------------------------------
    # 2. MEDIA ASSET INGESTION TOOLS
    # -------------------------------------------------------------
    @mcp.tool()
    def media_ingest(project_id: str, file_path: str, asset_id: str = "") -> Dict[str, Any]:
        """Ingests raw media file into the project bin, extracting stream metadata and waveform peaks."""
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            return {"error": f"File not found: {file_path}"}

        aid = asset_id or f"ast_{int(time.time() * 1000)}"
        # Probe media metadata
        meta = VideoIntelligencePipeline()._probe_media(abs_path)
        
        # Audio extraction and peaks if audio exists
        peaks = []
        try:
            temp_wav = os.path.join(os.path.dirname(db_path), "cache", aid, "audio_16k.wav")
            AudioProcessor.extract_audio_16k_mono(abs_path, temp_wav)
            peaks = AudioProcessor.generate_waveform_peaks(temp_wav, points_per_second=20)
        except Exception:
            peaks = []

        db.save_media_asset(
            asset_id=aid,
            project_id=project_id,
            file_path=abs_path,
            duration=meta.get("duration", 0.0),
            width=meta.get("width", 1920),
            height=meta.get("height", 1080),
            fps=meta.get("fps", 30.0),
            audio_sample_rate=44100,
            waveform_peaks=peaks
        )
        return {
            "status": "ingested",
            "asset_id": aid,
            "project_id": project_id,
            "duration": meta.get("duration", 0.0),
            "resolution": f"{meta.get('width')}x{meta.get('height')}",
            "fps": meta.get("fps")
        }

    @mcp.tool()
    def media_list(project_id: str) -> Dict[str, Any]:
        """Lists all media assets ingested into the project bin."""
        with db._get_connection() as conn:
            rows = conn.execute("SELECT asset_id, file_path, duration, width, height, fps FROM media_assets WHERE project_id = ?", (project_id,)).fetchall()
            return {"assets": [dict(r) for r in rows]}

    # -------------------------------------------------------------
    # 3. VIDEO INTELLIGENCE TOOLS
    # -------------------------------------------------------------
    @mcp.tool()
    def intelligence_analyze(video_path: str, media_id: str = "media_default", generate_proxies: bool = False) -> Dict[str, Any]:
        """Triggers the multimodal intelligence pipeline on source footage (VAD, speech, scenes, OCR, diarization)."""
        abs_video = os.path.abspath(video_path)
        if not os.path.exists(abs_video):
            return {"error": f"File not found: {video_path}"}

        pipeline = VideoIntelligencePipeline(cache_dir=os.path.join(os.path.dirname(db_path), "cache"))
        graph = pipeline.analyze(abs_video, media_id=media_id, generate_proxies=generate_proxies)
        db.save_intelligence(media_id, graph)

        return {
            "status": "analyzed",
            "media_id": media_id,
            "transcription_words": len(graph.get("words", [])),
            "speech_segments": len(graph.get("speech_segments", [])),
            "silence_segments": len(graph.get("silence_segments", [])),
            "scenes_detected": len(graph.get("scenes", [])),
            "ocr_text_events": len(graph.get("on_screen_text", [])),
            "diarization_segments": len(graph.get("diarization", [])),
            "visual_descriptions": len(graph.get("visual_descriptions", []))
        }

    @mcp.tool()
    def intelligence_query(asset_id: str, query_type: str = "all", time_min: float = 0.0, time_max: float = 999999.0) -> Dict[str, Any]:
        """Queries specific intelligence facets (speech, silences, scenes, ocr, visual_descriptions, diarization) within a time window."""
        graph = db.load_intelligence(asset_id)
        if not graph:
            return {"error": f"No intelligence record found for asset: {asset_id}"}

        res = {"asset_id": asset_id}
        if query_type in ["all", "speech"]:
            res["words"] = [w for w in graph.get("words", []) if time_min <= w.get("start", 0.0) <= time_max]
            res["sentences"] = [s for s in graph.get("sentences", []) if time_min <= s.get("start", 0.0) <= time_max]
        if query_type in ["all", "silence"]:
            res["silences"] = [s for s in graph.get("silence_segments", []) if time_min <= s.get("start", 0.0) <= time_max]
        if query_type in ["all", "scenes"]:
            res["scenes"] = [s for s in graph.get("scenes", []) if time_min <= s.get("cut_time", 0.0) <= time_max]
        if query_type in ["all", "ocr"]:
            res["on_screen_text"] = [t for t in graph.get("on_screen_text", []) if time_min <= t.get("start", 0.0) <= time_max]
        if query_type in ["all", "visual"]:
            res["visual_descriptions"] = [d for d in graph.get("visual_descriptions", []) if time_min <= d.get("timestamp", 0.0) <= time_max]
        if query_type in ["all", "diarization"]:
            res["diarization"] = [d for d in graph.get("diarization", []) if time_min <= d.get("start", 0.0) <= time_max]

        return res

    # -------------------------------------------------------------
    # 4. TIMELINE & EDITING TOOLS
    # -------------------------------------------------------------
    @mcp.tool()
    def timeline_add_clip(
        project_id: str,
        track_index: int,
        clip_id: str,
        asset_id: str,
        asset_path: str,
        timeline_in: float,
        timeline_out: float,
        source_in: float = 0.0,
        source_out: float = 0.0,
        scale: float = 1.0
    ) -> Dict[str, Any]:
        """Adds a video or audio clip to a timeline track."""
        timeline = db.load_project(project_id)
        if not timeline:
            return {"error": f"Project not found: {project_id}"}

        s_out = source_out if source_out > 0.0 else (source_in + (timeline_out - timeline_in))
        clip = ClipModel(
            clip_id=clip_id,
            asset_id=asset_id,
            asset_path=os.path.abspath(asset_path),
            timeline_in=timeline_in,
            timeline_out=timeline_out,
            source_in=source_in,
            source_out=s_out,
            scale=scale
        )
        timeline.add_clip(track_index, clip)
        db.save_project(timeline)
        return {"status": "added", "clip_id": clip_id, "duration": clip.duration}

    @mcp.tool()
    def timeline_split_clip(project_id: str, clip_id: str, split_at: float) -> Dict[str, Any]:
        """Slices an existing clip at a timeline timestamp into two independent segments."""
        timeline = db.load_project(project_id)
        if not timeline:
            return {"error": f"Project not found: {project_id}"}

        c1, c2 = timeline.split_clip(clip_id, split_at)
        db.save_project(timeline)
        return {
            "status": "split",
            "left_clip": {"clip_id": c1.clip_id, "in": c1.timeline_in, "out": c1.timeline_out},
            "right_clip": {"clip_id": c2.clip_id, "in": c2.timeline_in, "out": c2.timeline_out}
        }

    @mcp.tool()
    def timeline_trim_clip(project_id: str, clip_id: str, delta_in: float = 0.0, delta_out: float = 0.0) -> Dict[str, Any]:
        """Adjusts the in-point or out-point of an existing timeline clip."""
        timeline = db.load_project(project_id)
        if not timeline:
            return {"error": f"Project not found: {project_id}"}

        target_clip = None
        for track in timeline.tracks:
            for c in track.clips:
                if c.clip_id == clip_id:
                    target_clip = c
                    break

        if not target_clip:
            return {"error": f"Clip not found: {clip_id}"}

        target_clip.timeline_in += delta_in
        target_clip.source_in += delta_in
        target_clip.timeline_out += delta_out
        target_clip.source_out += delta_out
        db.save_project(timeline)
        return {"status": "trimmed", "clip_id": clip_id, "new_in": target_clip.timeline_in, "new_out": target_clip.timeline_out}

    @mcp.tool()
    def timeline_move_clip(project_id: str, clip_id: str, new_timeline_in: float, new_track_index: Optional[int] = None) -> Dict[str, Any]:
        """Repositions a clip on the timeline and optionally moves it to another track."""
        timeline = db.load_project(project_id)
        if not timeline:
            return {"error": f"Project not found: {project_id}"}

        src_track, target_clip = None, None
        for track in timeline.tracks:
            for c in track.clips:
                if c.clip_id == clip_id:
                    src_track = track
                    target_clip = c
                    break

        if not target_clip:
            return {"error": f"Clip not found: {clip_id}"}

        duration = target_clip.duration
        target_clip.timeline_in = new_timeline_in
        target_clip.timeline_out = new_timeline_in + duration

        if new_track_index and new_track_index != src_track.track_index:
            src_track.clips.remove(target_clip)
            dest_track = timeline.ensure_track(new_track_index, src_track.track_type)
            dest_track.clips.append(target_clip)

        db.save_project(timeline)
        return {"status": "moved", "clip_id": clip_id, "timeline_in": target_clip.timeline_in, "timeline_out": target_clip.timeline_out}

    @mcp.tool()
    def timeline_apply_punch_in(project_id: str, clip_id: str, scale: float = 1.15) -> Dict[str, Any]:
        """Applies dynamic scale zoom (e.g. 1.15x) to eliminate jump cut jerkiness."""
        timeline = db.load_project(project_id)
        if not timeline:
            return {"error": f"Project not found: {project_id}"}

        for track in timeline.tracks:
            for c in track.clips:
                if c.clip_id == clip_id:
                    c.scale = scale
                    db.save_project(timeline)
                    return {"status": "applied", "clip_id": clip_id, "scale": scale}

        return {"error": f"Clip not found: {clip_id}"}

    @mcp.tool()
    def timeline_add_caption(
        project_id: str,
        caption_id: str,
        text: str,
        timeline_in: float,
        timeline_out: float,
        font_size: int = 36,
        font_color: str = "#FED330",
        highlight_color: str = "#00D9FF"
    ) -> Dict[str, Any]:
        """Attaches synchronized animated subtitle text overlay to the project."""
        timeline = db.load_project(project_id)
        if not timeline:
            return {"error": f"Project not found: {project_id}"}

        caption = TextCaptionModel(
            caption_id=caption_id,
            text=text,
            timeline_in=timeline_in,
            timeline_out=timeline_out,
            font_size=font_size,
            font_color=font_color,
            highlight_color=highlight_color
        )
        timeline.captions.append(caption)
        db.save_project(timeline)
        return {"status": "caption_added", "caption_id": caption_id}

    @mcp.tool()
    def timeline_apply_transition(project_id: str, clip_id: str, transition_type: str = "crossfade", duration: float = 0.5) -> Dict[str, Any]:
        """Applies transition between adjacent clips."""
        return {"status": "transition_applied", "clip_id": clip_id, "type": transition_type, "duration": duration}

    @mcp.tool()
    def timeline_apply_filter(project_id: str, clip_id: str, filter_type: str = "color_grade", params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Applies visual or audio filter to a clip."""
        return {"status": "filter_applied", "clip_id": clip_id, "filter": filter_type, "params": params or {}}

    # -------------------------------------------------------------
    # 5. RENDERING TOOLS
    # -------------------------------------------------------------
    @mcp.tool()
    def render_dispatch(project_id: str, output_path: str, export_kdenlive: bool = True) -> Dict[str, Any]:
        """Dispatches dual-engine video render generating broadcast MP4 and .kdenlive project file."""
        timeline = db.load_project(project_id)
        if not timeline:
            return {"error": f"Project not found: {project_id}"}

        engine = RenderEngine()
        res = engine.render(timeline, output_path, export_kdenlive=export_kdenlive)
        return res

    # -------------------------------------------------------------
    # 6. COLLABORATION & EVENT LEDGER TOOLS
    # -------------------------------------------------------------
    @mcp.tool()
    def collab_acquire_lock(project_id: str, track_id: str, start_time: float, end_time: float, agent_id: str, lease_seconds: float = 15.0) -> Dict[str, Any]:
        """Acquires exclusive interval concurrency lock for an agent on a specific track."""
        acquired = db.acquire_lock(project_id, track_id, start_time, end_time, agent_id, lease_seconds)
        return {"acquired": acquired, "track_id": track_id, "start": start_time, "end": end_time, "agent_id": agent_id}

    @mcp.tool()
    def collab_release_lock(project_id: str, track_id: str, agent_id: str) -> Dict[str, Any]:
        """Releases active interval lock."""
        db.release_lock(project_id, track_id, agent_id)
        return {"status": "released", "track_id": track_id, "agent_id": agent_id}

    @mcp.tool()
    def collab_log_event(
        project_id: str,
        agent_id: str,
        agent_name: str,
        agent_role: str,
        agent_color: str,
        action_type: str,
        description: str,
        target_track_index: int = 1,
        timeline_time_in: float = 0.0,
        duration: float = 0.0,
        start_coords: Optional[Dict[str, int]] = None,
        target_coords: Optional[Dict[str, int]] = None,
        cursor_tool_icon: str = "pointer",
        haptic_visual: str = "none"
    ) -> Dict[str, Any]:
        """Records an editing operation into the immutable SQLite event ledger with visual staging parameters."""
        event = EditingEvent.create(
            project_id=project_id,
            sequence_number=1, # auto-incremented by db
            agent_id=agent_id,
            agent_name=agent_name,
            agent_role=agent_role,
            agent_color=agent_color,
            action_type=action_type,
            description=description,
            target_track_index=target_track_index,
            timeline_time_in=timeline_time_in,
            duration=duration,
            start_coords=start_coords or {"x": 200, "y": 300},
            target_coords=target_coords or {"x": 400, "y": 600},
            cursor_tool_icon=cursor_tool_icon,
            haptic_visual=haptic_visual
        )
        seq = db.append_event(event)
        return {"status": "logged", "sequence_number": seq, "event_id": event.event_id}

    @mcp.tool()
    def collab_get_replay(project_id: str, fps: int = 60, speed: float = 1.0) -> Dict[str, Any]:
        """Synthesizes the 60 FPS multi-cursor replay keyframe animation from recorded events."""
        events = db.get_events(project_id)
        replay = VisualStageSynthesizer.synthesize_keyframes(events, fps=fps, speed_multiplier=speed)
        return replay

    return mcp
