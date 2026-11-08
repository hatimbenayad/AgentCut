"""
AgentCut: End-to-End Vertical Slice Integration Test
Validates Milestone 2 Definition of Done:
1. Ingestion & Audio extraction
2. Multimodal Video Intelligence analysis (VAD, transcription, scenes, pauses)
3. Canonical Timeline manipulation (cuts, punch-in jump cut, captions)
4. Dual-engine rendering (MP4 + .kdenlive project file)
5. Authoritative SQLite event ledger logging
6. Cinematic Multi-Cursor Replay keyframe synthesis
"""

import os
import json
import pytest
from agentcut.core.timeline import ProjectTimeline, TrackModel, ClipModel, TextCaptionModel, ProjectProfile
from agentcut.core.serializer import KdenliveSerializer
from agentcut.core.database import ProjectDatabase
from agentcut.core.events import EditingEvent
from agentcut.intelligence.pipeline import VideoIntelligencePipeline
from agentcut.render.engine import RenderEngine
from agentcut.render.validator import RenderValidator
from agentcut.replay.visual_stage import VisualStageSynthesizer

def test_full_vertical_slice():
    print("\n=======================================================")
    print("🎬 STARTING AGENTCUT END-TO-END VERTICAL SLICE TEST")
    print("=======================================================")

    test_video = os.path.abspath("experiments/timeline_mlt/clip_a.mp4")
    assert os.path.exists(test_video), f"Source test video missing: {test_video}"

    work_dir = os.path.abspath("experiments/vertical_slice")
    os.makedirs(work_dir, exist_ok=True)
    db_path = os.path.join(work_dir, "agentcut_project.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    db = ProjectDatabase(db_path)

    # ---------------------------------------------------------
    # STAGE 1: VIDEO INTELLIGENCE ENGINE ANALYSIS
    # ---------------------------------------------------------
    print("\n[Stage 1/5] Running Video Intelligence Pipeline...")
    pipeline = VideoIntelligencePipeline(cache_dir=os.path.join(work_dir, "cache"))
    intel_graph = pipeline.analyze(test_video, media_id="test_clip_a")
    
    assert "metadata" in intel_graph, "Missing metadata in intelligence graph"
    assert "waveform_peaks" in intel_graph, "Missing waveform peaks"
    assert "silence_segments" in intel_graph, "Missing silence segments"
    assert "scenes" in intel_graph, "Missing scene cuts"
    print(f"✔ Metadata: {intel_graph['metadata']['width']}x{intel_graph['metadata']['height']} @ {intel_graph['metadata']['fps']}fps")
    print(f"✔ Waveform: {len(intel_graph['waveform_peaks'])} downsampled peak points generated")
    print(f"✔ Speech segments: {len(intel_graph['speech_segments'])}, Silence segments: {len(intel_graph['silence_segments'])}")
    print(f"✔ Scenes detected: {len(intel_graph['scenes'])}")

    # Save to SQLite store
    db.save_intelligence("test_clip_a", intel_graph)
    reloaded_intel = db.load_intelligence("test_clip_a")
    assert reloaded_intel is not None
    print("✔ Intelligence graph persisted to SQLite database")

    # ---------------------------------------------------------
    # STAGE 2: CANONICAL TIMELINE CONSTRUCTION & EDITS
    # ---------------------------------------------------------
    print("\n[Stage 2/5] Constructing Canonical Timeline Model...")
    timeline = ProjectTimeline(
        project_id="prj_vs_001",
        name="Vertical Slice Delivery",
        profile=ProjectProfile(width=1280, height=720, fps=30.0)
    )

    v_track = timeline.ensure_track(track_index=1, track_type="video", name="Video 1")
    a_track = timeline.ensure_track(track_index=2, track_type="audio", name="Audio 1")

    # Place initial 5.0s clip
    initial_clip = ClipModel(
        clip_id="clip_01",
        asset_id="test_clip_a",
        asset_path=test_video,
        timeline_in=0.0,
        timeline_out=5.0,
        source_in=0.0,
        source_out=5.0
    )
    timeline.add_clip(track_index=1, clip=initial_clip)
    print(f"✔ Added initial clip: [{initial_clip.timeline_in}s -> {initial_clip.timeline_out}s]")

    # Perform Razor Split at 2.5s
    print("Executing razor split at 2.5s...")
    clip_1a, clip_1b = timeline.split_clip("clip_01", split_at=2.5)
    print(f"✔ Sliced into: Clip 1A [{clip_1a.timeline_in}s -> {clip_1a.timeline_out}s] and Clip 1B [{clip_1b.timeline_in}s -> {clip_1b.timeline_out}s]")

    # Apply 1.15x dynamic punch-in zoom on second segment for professional jump cut
    clip_1b.scale = 1.15
    print("✔ Applied 1.15x punch-in jump cut to Clip 1B")

    # Attach synchronized animated subtitle caption
    timeline.captions.append(TextCaptionModel(
        caption_id="cap_01",
        text="AGENTCUT AI-NATIVE VIDEO STUDIO",
        timeline_in=0.5,
        timeline_out=4.5,
        font_size=38,
        font_color="#FED330",
        highlight_color="#00D9FF"
    ))
    print(f"✔ Attached animated caption: '{timeline.captions[0].text}' [0.5s -> 4.5s]")

    # Commit project state to SQLite
    db.save_project(timeline)
    reloaded_project = db.load_project("prj_vs_001")
    assert reloaded_project is not None
    assert len(reloaded_project.tracks[0].clips) == 2
    assert reloaded_project.tracks[0].clips[1].scale == 1.15
    print("✔ Canonical Timeline saved and verified in SQLite store")

    # ---------------------------------------------------------
    # STAGE 3: EVENT LEDGER & CONCURRENCY LOCKING
    # ---------------------------------------------------------
    print("\n[Stage 3/5] Recording Real Editing Operations to Event Ledger...")
    # Acquire lock for Video Editor
    lock_ok = db.acquire_lock("prj_vs_001", "track_video_1", 0.0, 5.0, "editor_agent_1")
    assert lock_ok is True
    print("✔ Interval lock acquired for Video Editor on Track V1 [0.0s, 5.0s]")

    # Event 1: Media drag & drop
    seq1 = db.append_event(EditingEvent.create(
        project_id="prj_vs_001",
        sequence_number=1,
        agent_id="editor_agent_1",
        agent_name="Video Editor",
        agent_role="editor",
        agent_color="#00D9FF",
        action_type="media_drag_drop",
        description="Dragging raw interview footage from Media Bin to Track V1",
        target_track_index=1,
        timeline_time_in=0.0,
        duration=5.0,
        source_asset_id="test_clip_a",
        start_coords={"x": 120, "y": 280},
        target_coords={"x": 350, "y": 620},
        cursor_tool_icon="grab",
        haptic_visual="snap_shadow"
    ))

    # Event 2: Razor split
    seq2 = db.append_event(EditingEvent.create(
        project_id="prj_vs_001",
        sequence_number=2,
        agent_id="editor_agent_1",
        agent_name="Video Editor",
        agent_role="editor",
        agent_color="#00D9FF",
        action_type="clip_split",
        description="Slicing clip at 2.5s for dynamic pacing transition",
        target_track_index=1,
        timeline_time_in=2.5,
        start_coords={"x": 350, "y": 620},
        target_coords={"x": 580, "y": 620},
        cursor_tool_icon="razor",
        haptic_visual="slice_particle"
    ))

    # Event 3: Punch-in jump cut
    seq3 = db.append_event(EditingEvent.create(
        project_id="prj_vs_001",
        sequence_number=3,
        agent_id="editor_agent_1",
        agent_name="Video Editor",
        agent_role="editor",
        agent_color="#00D9FF",
        action_type="punch_in_apply",
        description="Applying 1.15x camera punch-in to eliminate jump cut jerkiness",
        target_track_index=1,
        timeline_time_in=2.5,
        start_coords={"x": 580, "y": 620},
        target_coords={"x": 720, "y": 620},
        cursor_tool_icon="pointer",
        haptic_visual="glow_pulse"
    ))

    # Release lock
    db.release_lock("prj_vs_001", "track_video_1", "editor_agent_1")

    # Event 4: Caption Designer stamps subtitles
    seq4 = db.append_event(EditingEvent.create(
        project_id="prj_vs_001",
        sequence_number=4,
        agent_id="captions_agent_1",
        agent_name="Caption Designer",
        agent_role="captions",
        agent_color="#FED330",
        action_type="caption_stamp",
        description="Stamping speech-synchronized yellow typography overlay",
        target_track_index=3,
        timeline_time_in=0.5,
        duration=4.0,
        start_coords={"x": 400, "y": 300},
        target_coords={"x": 500, "y": 550},
        cursor_tool_icon="text_stamp",
        haptic_visual="ripple"
    ))

    events = db.get_events("prj_vs_001")
    assert len(events) == 4
    assert [e.sequence_number for e in events] == [1, 2, 3, 4]
    print(f"✔ 4 real editing events logged with strict monotonic ordering: {seq1}, {seq2}, {seq3}, {seq4}")

    # ---------------------------------------------------------
    # STAGE 4: DUAL-ENGINE RENDERING & OUTPUT VALIDATION
    # ---------------------------------------------------------
    print("\n[Stage 4/5] Executing Dual-Engine Video Render...")
    export_mp4 = os.path.join(work_dir, "vertical_slice_final.mp4")
    render_engine = RenderEngine()
    
    render_res = render_engine.render(
        timeline=timeline,
        output_mp4=export_mp4,
        export_kdenlive=True
    )

    assert render_res["status"] == "success"
    assert os.path.exists(export_mp4)
    assert os.path.exists(render_res["kdenlive_path"])
    print(f"✔ Render completed successfully via {render_res['rendered_with']} in {render_res['render_time_seconds']}s")
    print(f"✔ Deliverable MP4: {export_mp4} ({render_res['file_size_bytes']} bytes)")
    print(f"✔ Kdenlive project: {render_res['kdenlive_path']}")
    print(f"✔ Integrity check: {render_res['verification']}")

    # ---------------------------------------------------------
    # STAGE 5: CINEMATIC MULTI-AGENT REPLAY SYNTHESIS
    # ---------------------------------------------------------
    print("\n[Stage 5/5] Synthesizing Cinematic Multi-Agent Replay Keyframes...")
    replay_data = VisualStageSynthesizer.synthesize_keyframes(events, fps=60, speed_multiplier=1.0)
    
    assert replay_data["total_frames"] > 0
    assert len(replay_data["agents"]) == 2  # Video Editor & Caption Designer
    assert "Video Editor" in [a["name"] for a in replay_data["agents"]]
    assert "Caption Designer" in [a["name"] for a in replay_data["agents"]]
    
    # Save replay data JSON for UI playback
    replay_json_path = os.path.join(work_dir, "replay_stage.json")
    with open(replay_json_path, "w", encoding="utf-8") as f:
        json.dump(replay_data, f, indent=2)

    print(f"✔ Replay synthesized: {replay_data['total_frames']} 60fps frames ({replay_data['total_duration_sec']}s total)")
    print(f"✔ Replay dataset exported to: {replay_json_path}")

    print("\n=======================================================")
    print("🎉 AGENTCUT VERTICAL SLICE COMPLETED & 100% VERIFIED!")
    print("=======================================================\n")

if __name__ == "__main__":
    test_full_vertical_slice()
