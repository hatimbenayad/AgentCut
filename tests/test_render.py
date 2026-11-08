"""
Unit Tests: Dual-Engine Renderer & Output Validation
"""

import os
import pytest
from agentcut.core.timeline import ProjectTimeline, ClipModel, ProjectProfile
from agentcut.render.engine import RenderEngine
from agentcut.render.validator import RenderValidator

def test_render_validation_failure():
    # Non-existent file
    ok, msg = RenderValidator.verify("non_existent_file.mp4", 5.0)
    assert ok is False
    assert "does not exist" in msg

def test_timeline_render():
    test_video = os.path.abspath("experiments/timeline_mlt/clip_a.mp4")
    if not os.path.exists(test_video):
        pytest.skip("Test video clip_a.mp4 not found")

    out_dir = os.path.abspath("experiments/unit_renders")
    os.makedirs(out_dir, exist_ok=True)
    out_mp4 = os.path.join(out_dir, "test_render.mp4")

    timeline = ProjectTimeline(
        project_id="prj_render_test",
        name="Render Unit Test",
        profile=ProjectProfile(width=640, height=360, fps=30.0)
    )
    timeline.ensure_track(1, "video", "V1")
    timeline.add_clip(1, ClipModel("c1", "a1", test_video, 0.0, 2.0, 0.0, 2.0))

    engine = RenderEngine()
    res = engine.render(timeline, out_mp4, export_kdenlive=True)

    assert res["status"] == "success"
    assert os.path.exists(out_mp4)
    assert os.path.getsize(out_mp4) > 1000
    assert os.path.exists(res["kdenlive_path"])
