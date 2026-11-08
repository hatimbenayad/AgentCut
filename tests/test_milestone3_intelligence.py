"""
Tests for Milestone 3: Deepened Intelligence Pipeline & Proxy Previews
Spec reference: docs/specs/video-intelligence/spec.md
"""

import os
import pytest
import subprocess
import numpy as np
from PIL import Image

from agentcut.intelligence.proxy import ProxyGenerator
from agentcut.intelligence.diarization import SpeakerDiarizer, DiarizationSegment
from agentcut.intelligence.vision_adapter import VisionIntelligenceAdapter, VisualDescription
from agentcut.intelligence.chunker import LongVideoChunker, VideoChunk
from agentcut.intelligence.pipeline import VideoIntelligencePipeline

@pytest.fixture(scope="module")
def sample_video(tmp_path_factory):
    """Generates a short synthetic MP4 video with speech-like tones for testing."""
    test_dir = tmp_path_factory.mktemp("m3_test")
    vid_path = os.path.join(test_dir, "m3_sample.mp4")

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "testsrc=duration=3:size=640x360:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        vid_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert os.path.exists(vid_path)
    return str(vid_path)

def test_proxy_generation(sample_video, tmp_path):
    proxy_out = os.path.join(tmp_path, "proxy_360p.mp4")
    res = ProxyGenerator.generate_proxy_video(sample_video, proxy_out, target_height=360)

    assert os.path.exists(res)
    assert os.path.getsize(res) > 1024

    # Verify container faststart and stream duration via ffprobe
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=codec_name,width,height",
        "-of", "json",
        res
    ]
    p_res = subprocess.run(probe_cmd, capture_output=True, text=True)
    assert p_res.returncode == 0
    assert "h264" in p_res.stdout.lower()

def test_thumbnail_strip(sample_video, tmp_path):
    thumb_dir = os.path.join(tmp_path, "thumbs")
    thumbs = ProxyGenerator.generate_thumbnail_strip(sample_video, thumb_dir, interval_sec=1.0)

    assert len(thumbs) >= 2
    for th in thumbs:
        assert os.path.exists(th["path"])
        assert th["timestamp"] >= 0.0

def test_speaker_diarization(tmp_path):
    # Generate 4-second WAV with two distinct frequency tones simulating two alternating speakers
    wav_path = os.path.join(tmp_path, "multi_speaker.wav")
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "sine=frequency=220:duration=2",
        "-f", "lavfi", "-i", "sine=frequency=880:duration=2",
        "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[a]",
        "-map", "[a]",
        "-ar", "16000", "-ac", "1",
        wav_path
    ]
    subprocess.run(cmd, capture_output=True, text=True)

    diarizer = SpeakerDiarizer()
    segments = diarizer.diarize(wav_path, max_speakers=2)

    assert len(segments) >= 1
    assert all(isinstance(s, DiarizationSegment) for s in segments)

    # Test word association
    words = [
        {"word_id": "w_1", "text": "Hello", "start": 0.5, "end": 1.0},
        {"word_id": "w_2", "text": "World", "start": 2.5, "end": 3.0}
    ]
    associated = SpeakerDiarizer.assign_speakers_to_words(words, segments)
    assert "speaker" in associated[0]
    assert "speaker" in associated[1]

def test_vision_intelligence_adapter(tmp_path):
    # Create synthetic test frame
    img_path = os.path.join(tmp_path, "test_frame.jpg")
    img_data = np.zeros((360, 640, 3), dtype=np.uint8)
    img_data[:, :, 0] = 200  # Warm reddish tint
    img_data[:, :, 1] = 100
    img_data[:, :, 2] = 50
    im = Image.fromarray(img_data)
    im.save(img_path)

    adapter = VisionIntelligenceAdapter()
    records = [{"keyframe_path": img_path, "timestamp": 1.5, "scene_id": "scene_001"}]
    ocr_events = [{"text": "AgentCut Architecture", "start": 1.0, "end": 3.0}]

    descriptions = adapter.analyze_keyframes(records, ocr_events)
    assert len(descriptions) == 1
    d = descriptions[0]
    assert isinstance(d, VisualDescription)
    assert "warm" in d.lighting
    assert d.timestamp == 1.5

def test_long_video_chunker(tmp_path):
    chunker = LongVideoChunker(chunk_duration_sec=10.0, overlap_sec=2.0)
    
    # Simulate speech tokens from 2 chunks
    chunk_0 = VideoChunk(0, 0.0, 10.0, 0.0, "dummy_0.mp4")
    chunk_1 = VideoChunk(1, 8.0, 18.0, 2.0, "dummy_1.mp4")

    words_c0 = [
        {"word_id": "w_1", "text": "Start", "start": 1.0, "end": 2.0},
        {"word_id": "w_2", "text": "Overlap", "start": 8.5, "end": 9.5}
    ]
    words_c1 = [
        # In chunk 1, "Overlap" occurred at relative ts 0.5 (master 8.5)
        {"word_id": "w_1", "text": "Overlap", "start": 0.5, "end": 1.5},
        {"word_id": "w_2", "text": "Continue", "start": 3.0, "end": 4.0}
    ]

    master_words = chunker.reassemble_speech_events([
        (chunk_0, words_c0),
        (chunk_1, words_c1)
    ])

    # Overlapping duplicate token should be reconciled cleanly
    assert len(master_words) == 3
    assert master_words[0]["text"] == "Start"
    assert master_words[0]["start"] == 1.0
    assert master_words[1]["text"] == "Overlap"
    assert master_words[1]["start"] == 8.5
    assert master_words[2]["text"] == "Continue"
    assert master_words[2]["start"] == 11.0  # 8.0 offset + 3.0 relative

def test_pipeline_with_milestone3_features(sample_video, tmp_path):
    cache_dir = os.path.join(tmp_path, "pipeline_cache")
    pipeline = VideoIntelligencePipeline(cache_dir=cache_dir)

    result = pipeline.analyze(sample_video, media_id="test_m3_media", generate_proxies=True)

    assert result["media_id"] == "test_m3_media"
    assert "proxy_path" in result and result["proxy_path"] is not None
    assert os.path.exists(result["proxy_path"])
    assert "thumbnails" in result
    assert "diarization" in result
    assert "visual_descriptions" in result
    assert "waveform_peaks" in result
    assert len(result["waveform_peaks"]) > 0

