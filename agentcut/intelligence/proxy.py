"""
AgentCut Intelligence: Proxy Video & Thumbnail Pre-computation
Spec reference: docs/specs/video-intelligence/spec.md, docs/architecture/architecture-decisions.md (ADR-003)
"""

import os
import subprocess
import json
from typing import List, Dict, Any, Optional

class ProxyGenerator:
    """
    Generates low-latency, fast-scrub proxy videos and thumbnail visual assets
    for smooth timeline scrubbing in desktop and web UI.
    """

    @staticmethod
    def generate_proxy_video(
        input_video: str,
        output_proxy: str,
        target_height: int = 360,
        bitrate: str = "1000k",
        gop_size: int = 15
    ) -> str:
        """
        Creates an ultrafast low-resolution H.264 proxy with frequent keyframes (GOP=15)
        and faststart moov atom for instantaneous zero-stutter scrubbing.
        """
        if not os.path.exists(input_video):
            raise FileNotFoundError(f"Input video not found: {input_video}")

        os.makedirs(os.path.dirname(os.path.abspath(output_proxy)), exist_ok=True)

        # Scale height preserving aspect ratio, ensuring width is divisible by 2
        vf_scale = f"scale=-2:{target_height}:flags=fast_bilinear"

        cmd = [
            "ffmpeg", "-y",
            "-i", input_video,
            "-vf", vf_scale,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "fastdecode",
            "-b:v", bitrate,
            "-maxrate", bitrate,
            "-bufsize", "2000k",
            "-g", str(gop_size),          # Keyframe every 15 frames (~0.5s for 30fps)
            "-keyint_min", str(gop_size),
            "-sc_threshold", "0",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-ac", "2",
            "-movflags", "+faststart",
            output_proxy
        ]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg proxy generation failed:\n{res.stderr}")

        return output_proxy

    @staticmethod
    def generate_thumbnail_strip(
        input_video: str,
        output_dir: str,
        interval_sec: float = 2.0,
        thumb_height: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Extracts thumbnail images at fixed time intervals for the timeline canvas track preview.
        Returns a list of records with timestamp and image filepath.
        """
        if not os.path.exists(input_video):
            raise FileNotFoundError(f"Input video not found: {input_video}")

        os.makedirs(output_dir, exist_ok=True)

        # Query video duration via ffprobe
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_video
        ]
        duration_res = subprocess.run(probe_cmd, capture_output=True, text=True)
        duration = float(duration_res.stdout.strip()) if duration_res.stdout.strip() else 0.0

        if duration <= 0:
            return []

        # Generate timestamps
        timestamps = []
        t = 0.0
        while t < duration:
            timestamps.append(round(t, 2))
            t += interval_sec

        thumbnails = []
        for idx, ts in enumerate(timestamps):
            out_name = f"thumb_{idx:04d}_{int(ts*100):06d}.jpg"
            out_path = os.path.join(output_dir, out_name)

            cmd = [
                "ffmpeg", "-y",
                "-ss", str(ts),
                "-i", input_video,
                "-vframes", "1",
                "-vf", f"scale=-2:{thumb_height}:flags=fast_bilinear",
                "-q:v", "5",
                out_path
            ]
            subprocess.run(cmd, capture_output=True, text=True)
            if os.path.exists(out_path):
                thumbnails.append({
                    "index": idx,
                    "timestamp": ts,
                    "path": out_path
                })

        return thumbnails

