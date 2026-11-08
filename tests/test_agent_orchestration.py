"""
Unit & Integration Tests: Multi-Agent Orchestration & Concurrency Layer
Spec reference: docs/specs/agent-orchestration/spec.md
"""

import os
import pytest
from agentcut.core.database import ProjectDatabase
from agentcut.core.timeline import ProjectTimeline, ClipModel, ProjectProfile
from agentcut.orchestration.roles import AGENT_ROLES, BaseAgent
from agentcut.orchestration.coordinator import MultiAgentCoordinator

@pytest.fixture
def test_setup(tmp_path):
    db_path = os.path.join(tmp_path, "orchestration_test.db")
    db = ProjectDatabase(db_path)
    coordinator = MultiAgentCoordinator(db)
    test_video = os.path.abspath("experiments/timeline_mlt/clip_a.mp4")
    assert os.path.exists(test_video)
    return db, coordinator, test_video

def test_agent_roles_definition():
    expected_roles = ["director", "analyst", "editor", "audio", "captions", "colorist", "qc"]
    assert len(AGENT_ROLES) == 7
    for role_name in expected_roles:
        assert role_name in AGENT_ROLES
        role_cfg = AGENT_ROLES[role_name]
        assert role_cfg.name is not None
        assert role_cfg.color.startswith("#")
        assert len(role_cfg.color) == 7

def test_multi_agent_swarm_execution(test_setup):
    db, coordinator, test_video = test_setup
    project_id = "prj_swarm_001"

    prompt = "Create a punchy 45-second TikTok video with fast cuts, animated captions, and cinematic color."
    res = coordinator.execute_edit_brief(
        project_id=project_id,
        asset_id="ast_interview_01",
        asset_path=test_video,
        prompt=prompt,
        target_duration=5.0
    )

    assert res["status"] == "completed"
    assert res["qc_passed"] is True
    assert res["total_clips"] >= 2
    assert res["total_captions"] >= 1

    # Verify execution log
    log = res["execution_log"]
    agent_names_in_log = [entry["agent"] for entry in log]
    assert "Director" in agent_names_in_log
    assert "Footage Analyst" in agent_names_in_log
    assert "Video Editor" in agent_names_in_log
    assert "Audio Engineer" in agent_names_in_log
    assert "Caption Designer" in agent_names_in_log
    assert "Colorist" in agent_names_in_log
    assert "Quality Controller" in agent_names_in_log

def test_event_ledger_traceability(test_setup):
    db, coordinator, test_video = test_setup
    project_id = "prj_trace_001"

    coordinator.execute_edit_brief(
        project_id=project_id,
        asset_id="ast_interview_01",
        asset_path=test_video,
        prompt="Make a clean cut",
        target_duration=5.0
    )

    events = db.get_events(project_id)
    assert len(events) >= 7

    # Verify monotonic sequence ordering
    seqs = [e.sequence_number for e in events]
    assert seqs == list(range(1, len(events) + 1))

    # Verify visual staging on all events
    for e in events:
        assert e.agent.name is not None
        assert e.visual_staging.cursor_tool_icon in ["pointer", "grab", "razor", "text_stamp"]
        assert e.visual_staging.start_coords["x"] > 0
        assert e.visual_staging.target_coords["x"] > 0

def test_qc_gap_detection(tmp_path):
    db_path = os.path.join(tmp_path, "qc_test.db")
    db = ProjectDatabase(db_path)
    coordinator = MultiAgentCoordinator(db)

    # Construct timeline with intentional 1.0s black gap
    timeline = ProjectTimeline(
        project_id="prj_gap_test",
        name="Gap Test",
        profile=ProjectProfile(width=1280, height=720, fps=30.0)
    )
    v_track = timeline.ensure_track(1, "video", "V1")
    v_track.clips.append(ClipModel("c1", "a1", "dummy.mp4", 0.0, 2.0, 0.0, 2.0))
    v_track.clips.append(ClipModel("c2", "a1", "dummy.mp4", 3.0, 5.0, 3.0, 5.0)) # 1.0s gap from 2.0 to 3.0
    db.save_project(timeline)

    # Run coordinator
    res = coordinator.execute_edit_brief(
        project_id="prj_gap_test",
        asset_id="a1",
        asset_path="dummy.mp4",
        prompt="Check quality"
    )

    # In execute_edit_brief, editor replaces or rebuilds clips, ensuring gap-free timeline
    assert res["status"] == "completed"
    assert res["qc_passed"] is True
