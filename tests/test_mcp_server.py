"""
Unit & Integration Tests: Model Context Protocol (MCP) Server
Spec reference: docs/specs/mcp-server/spec.md
ADR reference: docs/architecture/architecture-decisions.md (ADR-010)
"""

import os
import json
import pytest
from agentcut.mcp.server import create_mcp_server

@pytest.fixture(scope="module")
def mcp_fixture(tmp_path_factory):
    test_dir = tmp_path_factory.mktemp("mcp_test")
    db_path = os.path.join(test_dir, "agentcut_mcp.db")
    server = create_mcp_server(db_path=db_path)
    return server, test_dir

async def call_mcp_tool(server, tool_name: str, args: dict = None) -> dict:
    """Helper to execute an MCP tool and deserialize JSON result."""
    res = await server.call_tool(tool_name, args or {})
    assert not res.is_error, f"MCP tool {tool_name} returned error: {res}"
    if res.content and len(res.content) > 0:
        return json.loads(res.content[0].text)
    return {}

@pytest.mark.anyio
async def test_mcp_tools_registration(mcp_fixture):
    server, _ = mcp_fixture
    tools = await server.list_tools()
    tool_names = [t.name for t in tools]
    expected_tools = [
        "project_create", "project_get", "project_save",
        "media_ingest", "media_list",
        "intelligence_analyze", "intelligence_query",
        "timeline_add_clip", "timeline_split_clip", "timeline_trim_clip",
        "timeline_move_clip", "timeline_apply_punch_in", "timeline_add_caption",
        "timeline_apply_transition", "timeline_apply_filter",
        "render_dispatch",
        "collab_acquire_lock", "collab_release_lock", "collab_log_event", "collab_get_replay"
    ]
    for expected in expected_tools:
        assert expected in tool_names, f"Missing MCP tool: {expected}"
    assert len(tool_names) >= 20

@pytest.mark.anyio
async def test_mcp_project_lifecycle(mcp_fixture):
    server, _ = mcp_fixture
    # 1. Create project
    res = await call_mcp_tool(server, "project_create", {
        "name": "TikTok Vertical Edit",
        "width": 1080,
        "height": 1920,
        "fps": 30.0
    })
    assert res["status"] == "created"
    pid = res["project_id"]
    assert pid.startswith("prj_")

    # 2. Get project state
    state = await call_mcp_tool(server, "project_get", {"project_id": pid})
    assert state["project_id"] == pid
    assert state["profile"]["width"] == 1080
    assert state["profile"]["height"] == 1920

    # 3. Save project
    save_res = await call_mcp_tool(server, "project_save", {"project_id": pid})
    assert save_res["status"] == "saved"

@pytest.mark.anyio
async def test_mcp_media_ingest_and_list(mcp_fixture):
    server, _ = mcp_fixture
    test_video = os.path.abspath("experiments/timeline_mlt/clip_a.mp4")
    assert os.path.exists(test_video)

    res = await call_mcp_tool(server, "media_ingest", {
        "project_id": "prj_test",
        "file_path": test_video,
        "asset_id": "ast_interview_01"
    })
    assert res["status"] == "ingested"
    assert res["asset_id"] == "ast_interview_01"

    res = await call_mcp_tool(server, "media_list", {"project_id": "prj_test"})
    assert "assets" in res
    assert len(res["assets"]) >= 1
    assert any(a["asset_id"] == "ast_interview_01" for a in res["assets"])

@pytest.mark.anyio
async def test_mcp_timeline_editing_workflow(mcp_fixture):
    server, _ = mcp_fixture
    test_video = os.path.abspath("experiments/timeline_mlt/clip_a.mp4")

    # 1. Create project
    p_res = await call_mcp_tool(server, "project_create", {
        "name": "Editing Test",
        "width": 1280,
        "height": 720,
        "fps": 30.0
    })
    pid = p_res["project_id"]

    # 2. Add clip
    add_res = await call_mcp_tool(server, "timeline_add_clip", {
        "project_id": pid,
        "track_index": 1,
        "clip_id": "c_01",
        "asset_id": "a_01",
        "asset_path": test_video,
        "timeline_in": 0.0,
        "timeline_out": 5.0,
        "source_in": 0.0,
        "source_out": 5.0
    })
    assert add_res["status"] == "added"

    # 3. Split clip
    split_res = await call_mcp_tool(server, "timeline_split_clip", {
        "project_id": pid,
        "clip_id": "c_01",
        "split_at": 2.5
    })
    assert split_res["status"] == "split"
    assert split_res["left_clip"]["out"] == 2.5
    assert split_res["right_clip"]["in"] == 2.5
    right_id = split_res["right_clip"]["clip_id"]

    # 4. Apply punch-in zoom to right clip
    punch_res = await call_mcp_tool(server, "timeline_apply_punch_in", {
        "project_id": pid,
        "clip_id": right_id,
        "scale": 1.15
    })
    assert punch_res["status"] == "applied"
    assert punch_res["scale"] == 1.15

    # 5. Add caption
    cap_res = await call_mcp_tool(server, "timeline_add_caption", {
        "project_id": pid,
        "caption_id": "cap_01",
        "text": "AGENTCUT MCP PROTOCOL",
        "timeline_in": 0.5,
        "timeline_out": 4.0
    })
    assert cap_res["status"] == "caption_added"

    # 6. Verify full state
    state = await call_mcp_tool(server, "project_get", {"project_id": pid})
    v1_track = next(t for t in state["tracks"] if t["track_index"] == 1)
    assert len(v1_track["clips"]) == 2
    assert len(state["captions"]) == 1

@pytest.mark.anyio
async def test_mcp_concurrency_locking(mcp_fixture):
    server, _ = mcp_fixture
    pid = "prj_lock_test"
    track = "track_v1"

    # Agent 1 acquires [0.0s, 5.0s]
    r1 = await call_mcp_tool(server, "collab_acquire_lock", {
        "project_id": pid,
        "track_id": track,
        "start_time": 0.0,
        "end_time": 5.0,
        "agent_id": "agent_editor",
        "lease_seconds": 10.0
    })
    assert r1["acquired"] is True

    # Agent 2 attempts overlapping lock [3.0s, 7.0s] -> MUST BE REJECTED
    r2 = await call_mcp_tool(server, "collab_acquire_lock", {
        "project_id": pid,
        "track_id": track,
        "start_time": 3.0,
        "end_time": 7.0,
        "agent_id": "agent_colorist",
        "lease_seconds": 10.0
    })
    assert r2["acquired"] is False

    # Agent 1 releases lock
    rel = await call_mcp_tool(server, "collab_release_lock", {
        "project_id": pid,
        "track_id": track,
        "agent_id": "agent_editor"
    })
    assert rel["status"] == "released"

    # Agent 2 attempts again -> SUCCEEDS
    r3 = await call_mcp_tool(server, "collab_acquire_lock", {
        "project_id": pid,
        "track_id": track,
        "start_time": 3.0,
        "end_time": 7.0,
        "agent_id": "agent_colorist",
        "lease_seconds": 10.0
    })
    assert r3["acquired"] is True

@pytest.mark.anyio
async def test_mcp_event_logging_and_replay(mcp_fixture):
    server, _ = mcp_fixture
    pid = "prj_replay_test"

    # Log 2 events
    e1 = await call_mcp_tool(server, "collab_log_event", {
        "project_id": pid,
        "agent_id": "editor_1",
        "agent_name": "Video Editor",
        "agent_role": "editor",
        "agent_color": "#00D9FF",
        "action_type": "media_drag_drop",
        "description": "Placing intro clip",
        "target_track_index": 1,
        "timeline_time_in": 0.0,
        "duration": 4.0
    })
    assert e1["status"] == "logged"
    assert e1["sequence_number"] == 1

    e2 = await call_mcp_tool(server, "collab_log_event", {
        "project_id": pid,
        "agent_id": "captions_1",
        "agent_name": "Caption Designer",
        "agent_role": "captions",
        "agent_color": "#FED330",
        "action_type": "caption_stamp",
        "description": "Adding dynamic typography",
        "target_track_index": 3,
        "timeline_time_in": 1.0,
        "duration": 3.0
    })
    assert e2["status"] == "logged"
    assert e2["sequence_number"] == 2

    # Query replay animation dataset
    replay = await call_mcp_tool(server, "collab_get_replay", {
        "project_id": pid,
        "fps": 60,
        "speed": 1.0
    })
    assert replay["total_frames"] > 0
    assert len(replay["agents"]) == 2
    assert "frames" in replay
