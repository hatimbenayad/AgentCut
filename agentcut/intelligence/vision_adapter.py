"""
AgentCut Intelligence: Semantic Visual Description & Scene Framing Adapter
Spec reference: docs/specs/video-intelligence/spec.md
"""

import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import numpy as np

try:
    from PIL import Image
except ImportError:
    Image = None

@dataclass
class VisualDescription:
    scene_id: str
    keyframe_path: str
    timestamp: float
    description: str
    shot_type: str            # "close_up", "medium_shot", "wide_shot", "screen_recording", "presentation"
    lighting: str             # "studio_balanced", "high_key", "low_key", "warm", "cool"
    tags: List[str]
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class VisionIntelligenceAdapter:
    """
    Analyzes sampled keyframe imagery to extract semantic descriptions,
    lighting characteristics, framing classifications, and shot types.
    """

    def __init__(self, model_endpoint: Optional[str] = None):
        self.model_endpoint = model_endpoint

    def analyze_keyframes(
        self,
        keyframe_records: List[Dict[str, Any]],
        ocr_events: Optional[List[Dict[str, Any]]] = None
    ) -> List[VisualDescription]:
        """
        Analyzes a set of keyframe records and produces structured visual scene descriptions.
        """
        descriptions = []
        ocr_events = ocr_events or []

        for kf in keyframe_records:
            path = kf.get("keyframe_path") or kf.get("path")
            ts = kf.get("timestamp", 0.0)
            scene_id = kf.get("scene_id", "scene_001")

            if not path or not os.path.exists(path):
                continue

            # Check if there are overlapping OCR text events around this timestamp
            relevant_ocr = [
                ev["text"] for ev in ocr_events
                if ev.get("start", 0.0) <= ts <= ev.get("end", ts + 2.0)
            ]

            desc = self._analyze_image(path, ts, scene_id, relevant_ocr)
            descriptions.append(desc)

        return descriptions

    def _analyze_image(
        self,
        image_path: str,
        timestamp: float,
        scene_id: str,
        ocr_texts: List[str]
    ) -> VisualDescription:
        """
        Extracts visual metrics from image pixels and generates scene descriptions.
        """
        if Image is None:
            return VisualDescription(
                scene_id=scene_id,
                keyframe_path=image_path,
                timestamp=timestamp,
                description="Visual scene capture",
                shot_type="medium_shot",
                lighting="studio_balanced",
                tags=["video_frame"],
                confidence=0.75
            )

        with Image.open(image_path) as img:
            rgb_img = img.convert("RGB")
            w, h = rgb_img.size
            img_arr = np.array(rgb_img, dtype=np.float32)

        # 1. Luminance & Contrast
        # Rec. 709 luma coefficients
        luma = 0.2126 * img_arr[:, :, 0] + 0.7152 * img_arr[:, :, 1] + 0.0722 * img_arr[:, :, 2]
        mean_luma = float(np.mean(luma))
        std_luma = float(np.std(luma))

        if mean_luma > 180:
            lighting = "high_key"
        elif mean_luma < 60:
            lighting = "low_key"
        else:
            lighting = "studio_balanced"

        # 2. Color Temperature (Red vs Blue balance)
        mean_r = float(np.mean(img_arr[:, :, 0]))
        mean_b = float(np.mean(img_arr[:, :, 2]))
        if mean_r > mean_b * 1.15:
            lighting = f"{lighting}_warm"
        elif mean_b > mean_r * 1.15:
            lighting = f"{lighting}_cool"

        # 3. Edge Complexity (detect screens vs continuous tone natural scenes)
        # Compute horizontal and vertical gradients
        diff_x = np.abs(np.diff(luma, axis=1))
        diff_y = np.abs(np.diff(luma, axis=0))
        edge_energy = float(np.mean(diff_x) + np.mean(diff_y))

        # 4. Shot type & semantic classification
        tags = []
        if len(ocr_texts) > 0 or edge_energy > 28.0:
            if len(ocr_texts) >= 3:
                shot_type = "presentation"
                tags.extend(["slides", "text_dense", "presentation"])
                summary = f"Presentation slide or structured document displaying '{ocr_texts[0][:40]}...'"
            else:
                shot_type = "screen_recording"
                tags.extend(["screen_capture", "ui_interface"])
                joined_txt = ", ".join(ocr_texts[:2])
                summary = f"Digital screen or graphic layout with on-screen text '{joined_txt}'"
        else:
            # Framing based on variance and central concentration
            center_h, center_w = int(h * 0.2), int(w * 0.2)
            center_patch = luma[center_h:h-center_h, center_w:w-center_w]
            center_var = float(np.var(center_patch))

            if center_var > 1200 and std_luma > 40:
                shot_type = "medium_shot"
                tags.extend(["on_camera_subject", "interview"])
                summary = f"Medium shot with subject framed against {lighting.replace('_', ' ')} background"
            elif mean_luma < 70:
                shot_type = "cinematic_portrait"
                tags.extend(["dramatic", "low_light"])
                summary = "Cinematic mood shot with focused subject lighting"
            else:
                shot_type = "wide_shot"
                tags.extend(["wide_angle", "environment"])
                summary = f"Wide shot displaying overall scene environment with {lighting.replace('_', ' ')} lighting"

        return VisualDescription(
            scene_id=scene_id,
            keyframe_path=image_path,
            timestamp=timestamp,
            description=summary,
            shot_type=shot_type,
            lighting=lighting,
            tags=tags,
            confidence=0.88
        )

