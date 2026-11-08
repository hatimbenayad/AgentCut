"""
AgentCut Render: Output Integrity Validator
Spec reference: docs/specs/rendering/spec.md
"""

import os
import json
import subprocess

class RenderValidator:
    """Verifies deliverable video integrity before marking rendering complete."""

    @staticmethod
    def verify(output_path: str, expected_duration: float, tolerance_sec: float = 0.3) -> tuple[bool, str]:
        if not os.path.exists(output_path):
            return False, f"Output file does not exist: {output_path}"

        size_bytes = os.path.getsize(output_path)
        if size_bytes < 10000:  # Minimum 10KB
            return False, f"Output file size is suspiciously small ({size_bytes} bytes)."

        # Probe file via ffprobe
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            output_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            return False, f"ffprobe failed to parse container headers:\n{res.stderr}"

        try:
            data = json.loads(res.stdout)
            format_info = data.get("format", {})
            actual_duration = float(format_info.get("duration", 0.0))
            streams = data.get("streams", [])

            has_video = any(s.get("codec_type") == "video" for s in streams)
            has_audio = any(s.get("codec_type") == "audio" for s in streams)

            if not has_video:
                return False, "Output file has no valid video stream."

            delta = abs(actual_duration - expected_duration)
            if delta > tolerance_sec:
                return False, f"Duration mismatch: expected {expected_duration:.2f}s, got {actual_duration:.2f}s (delta={delta:.2f}s)."

            return True, f"Verified: {size_bytes} bytes, duration={actual_duration:.2f}s, video={has_video}, audio={has_audio}"
        except Exception as e:
            return False, f"Metadata validation exception: {str(e)}"

