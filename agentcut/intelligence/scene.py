"""
AgentCut Intelligence: Scene Boundary Detection & Keyframe Extraction
Spec reference: docs/specs/video-intelligence/spec.md
"""

import os
import cv2
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from scenedetect import open_video, SceneManager, ContentDetector

@dataclass
class SceneBoundary:
    scene_id: str
    start: float
    end: float
    duration: float
    keyframe_timestamp: float
    keyframe_path: str
    description: str = "Detected visual scene cut"

class SceneDetector:
    """Detects visual scene transitions and extracts representative keyframe images."""

    def __init__(self, threshold: float = 27.0):
        self.threshold = threshold

    def detect_scenes(self, video_path: str, keyframes_cache_dir: str) -> List[SceneBoundary]:
        os.makedirs(keyframes_cache_dir, exist_ok=True)
        video = open_video(video_path)
        fps = video.frame_rate
        total_duration = video.duration.seconds

        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=self.threshold))
        scene_manager.detect_scenes(video)
        raw_scenes = scene_manager.get_scene_list()

        cap = cv2.VideoCapture(video_path)
        scene_boundaries: List[SceneBoundary] = []

        # If PySceneDetect detected zero hard cuts, treat entire video as 1 scene
        if not raw_scenes:
            kf_time = round(min(1.0, total_duration / 2.0), 3)
            kf_path = os.path.join(keyframes_cache_dir, "keyframe_scene_001.jpg")
            self._save_frame(cap, kf_time, kf_path)
            scene_boundaries.append(SceneBoundary(
                scene_id="scene_001",
                start=0.0,
                end=round(total_duration, 3),
                duration=round(total_duration, 3),
                keyframe_timestamp=kf_time,
                keyframe_path=kf_path
            ))
        else:
            for s_idx, (start_time, end_time) in enumerate(raw_scenes):
                t_start = round(start_time.get_seconds(), 3)
                t_end = round(end_time.get_seconds(), 3)
                kf_time = round(t_start + min(0.5, (t_end - t_start) / 2.0), 3)
                kf_path = os.path.join(keyframes_cache_dir, f"keyframe_scene_{s_idx+1:03d}.jpg")
                self._save_frame(cap, kf_time, kf_path)

                scene_boundaries.append(SceneBoundary(
                    scene_id=f"scene_{s_idx+1:03d}",
                    start=t_start,
                    end=t_end,
                    duration=round(t_end - t_start, 3),
                    keyframe_timestamp=kf_time,
                    keyframe_path=kf_path
                ))

        cap.release()
        return scene_boundaries

    def _save_frame(self, cap: cv2.VideoCapture, timestamp_sec: float, output_path: str):
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_sec * 1000.0)
        ret, frame = cap.read()
        if ret and frame is not None:
            cv2.imwrite(output_path, frame)
