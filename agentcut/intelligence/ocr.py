"""
AgentCut Intelligence: RapidOCR (ONNX) with Temporal Box Tracking
Spec reference: docs/specs/video-intelligence/spec.md
ADR reference: docs/architecture/architecture-decisions.md (ADR-004, ADR-013)
"""

import os
import cv2
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

@dataclass
class DetectedTextEvent:
    text_id: str
    text: str
    start: float
    end: float
    confidence: float
    bounding_box: List[int] # [x1, y1, x2, y2]

class OCREngine:
    """Extracts on-screen text with temporal tracking and deduplication."""

    def __init__(self):
        self._engine = None

    def _get_engine(self):
        if self._engine is None:
            from rapidocr_onnxruntime import RapidOCR
            self._engine = RapidOCR()
        return self._engine

    def detect_on_frames(self, keyframe_records: List[tuple[float, str]]) -> List[DetectedTextEvent]:
        """Runs OCR on a list of (timestamp_sec, image_path) and tracks text temporally."""
        engine = self._get_engine()
        raw_events = []

        for t_sec, img_path in sorted(keyframe_records, key=lambda x: x[0]):
            if not os.path.exists(img_path):
                continue
            img = cv2.imread(img_path)
            if img is None:
                continue

            results, _ = engine(img)
            if results:
                for res in results:
                    box, text, conf = res
                    # Convert 4-point polygon to [x1, y1, x2, y2]
                    pts = np.array(box, dtype=np.int32)
                    x1 = int(np.min(pts[:, 0]))
                    y1 = int(np.min(pts[:, 1]))
                    x2 = int(np.max(pts[:, 0]))
                    y2 = int(np.max(pts[:, 1]))

                    raw_events.append({
                        "timestamp": t_sec,
                        "text": text.strip(),
                        "confidence": float(conf),
                        "box": [x1, y1, x2, y2]
                    })

        # Deduplicate and track temporally across frames
        return self._temporal_track(raw_events)

    def _temporal_track(self, raw_events: List[Dict[str, Any]]) -> List[DetectedTextEvent]:
        tracked: List[DetectedTextEvent] = []
        if not raw_events:
            return []

        # Group by string similarity and box IoU
        events_by_time = sorted(raw_events, key=lambda e: e["timestamp"])
        active_tracks: List[Dict[str, Any]] = []

        for evt in events_by_time:
            matched = False
            for trk in active_tracks:
                # Text similarity
                text_match = (
                    trk["text"].lower() in evt["text"].lower() or 
                    evt["text"].lower() in trk["text"].lower() or
                    self._levenshtein_ratio(trk["text"], evt["text"]) > 0.75
                )
                iou = self._calculate_iou(trk["box"], evt["box"])
                
                # If same text or high IoU within 4.0s
                if (text_match or iou > 0.5) and (evt["timestamp"] - trk["end"] <= 4.0):
                    trk["end"] = evt["timestamp"]
                    trk["conf_sum"] += evt["confidence"]
                    trk["count"] += 1
                    matched = True
                    break

            if not matched:
                active_tracks.append({
                    "text": evt["text"],
                    "start": evt["timestamp"],
                    "end": evt["timestamp"] + 1.5, # Default visibility estimate
                    "conf_sum": evt["confidence"],
                    "count": 1,
                    "box": evt["box"]
                })

        for idx, trk in enumerate(active_tracks):
            tracked.append(DetectedTextEvent(
                text_id=f"ocr_txt_{idx+1:03d}",
                text=trk["text"],
                start=round(trk["start"], 3),
                end=round(trk["end"], 3),
                confidence=round(trk["conf_sum"] / trk["count"], 3),
                bounding_box=trk["box"]
            ))

        return tracked

    @staticmethod
    def _calculate_iou(boxA: List[int], boxB: List[int]) -> float:
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        inter_area = max(0, xB - xA) * max(0, yB - yA)
        areaA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        areaB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        union_area = float(areaA + areaB - inter_area)
        return inter_area / union_area if union_area > 0 else 0.0

    @staticmethod
    def _levenshtein_ratio(s1: str, s2: str) -> float:
        s1, s2 = s1.lower(), s2.lower()
        if s1 == s2:
            return 1.0
        len_max = max(len(s1), len(s2))
        if len_max == 0:
            return 1.0
        # Simple character overlap ratio
        common = sum(1 for c in s1 if c in s2)
        return common / len_max
