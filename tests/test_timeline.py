"""
Unit Tests: Canonical Timeline Model & Serialization
"""

import pytest
from agentcut.core.timeline import ProjectTimeline, TrackModel, ClipModel, TextCaptionModel, ProjectProfile
from agentcut.core.serializer import KdenliveSerializer

def test_timeline_invariants():
    timeline = ProjectTimeline(
        project_id="prj_unit_01",
        name="Invariant Test",
        profile=ProjectProfile(width=1920, height=1080, fps=30.0)
    )

    track = timeline.ensure_track(1, "video", "V1")
    clip = ClipModel(
        clip_id="c1",
        asset_id="a1",
        asset_path="dummy.mp4",
        timeline_in=0.0,
        timeline_out=10.0,
        source_in=0.0,
        source_out=10.0
    )
    timeline.add_clip(1, clip)

    # Invariant: duration
    assert timeline.duration == 10.0

    # Invariant: split preserves total duration
    c1a, c1b = timeline.split_clip("c1", split_at=4.0)
    assert c1a.duration + c1b.duration == 10.0
    assert c1a.source_out == 4.0
    assert c1b.source_in == 4.0
    assert timeline.duration == 10.0

def test_json_roundtrip():
    timeline = ProjectTimeline(
        project_id="prj_unit_02",
        name="JSON Roundtrip",
        profile=ProjectProfile(width=1080, height=1920, aspect_ratio="9:16")
    )
    timeline.ensure_track(1, "video", "V1")
    timeline.add_clip(1, ClipModel("c1", "a1", "sample.mp4", 0.0, 5.0, 0.0, 5.0, scale=1.15))
    timeline.captions.append(TextCaptionModel("cap1", "Hello World", 1.0, 4.0))

    json_str = timeline.to_json()
    reloaded = ProjectTimeline.from_json(json_str)

    assert reloaded.project_id == timeline.project_id
    assert reloaded.profile.width == 1080
    assert reloaded.profile.height == 1920
    assert len(reloaded.tracks[0].clips) == 1
    assert reloaded.tracks[0].clips[0].scale == 1.15
    assert len(reloaded.captions) == 1
    assert reloaded.captions[0].text == "Hello World"

def test_kdenlive_xml_serialization():
    timeline = ProjectTimeline(
        project_id="prj_unit_03",
        name="Kdenlive XML Test",
        profile=ProjectProfile(width=1920, height=1080, fps=30.0)
    )
    timeline.ensure_track(1, "video", "V1")
    timeline.add_clip(1, ClipModel("c1", "a1", "sample.mp4", 0.0, 3.0, 0.0, 3.0))

    xml_str = KdenliveSerializer.to_mlt_xml(timeline)
    assert "<mlt" in xml_str
    assert 'title="Kdenlive XML Test"' in xml_str
    assert "<tractor id=\"maintractor\"" in xml_str
    assert "playlist_track_video_1" in xml_str
