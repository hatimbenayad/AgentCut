"""
AgentCut Render: Dual-Engine Render Controller (melt + FFmpeg)
Spec reference: docs/specs/rendering/spec.md
ADR reference: docs/architecture/architecture-decisions.md (ADR-002, ADR-009)
"""

import os
import shutil
import subprocess
import time
from typing import Optional, Callable, Dict, Any
from agentcut.core.timeline import ProjectTimeline
from agentcut.core.serializer import KdenliveSerializer
from agentcut.core.compiler import FFmpegCompiler
from agentcut.render.validator import RenderValidator

class RenderEngine:
    """Manages video rendering via headless MLT melt or native FFmpeg filtergraphs."""

    def __init__(self, melt_path: Optional[str] = None):
        self.melt_path = melt_path or shutil.which("melt")

    def render(
        self,
        timeline: ProjectTimeline,
        output_mp4: str,
        export_kdenlive: bool = True,
        use_nvenc: bool = False,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        abs_output = os.path.abspath(output_mp4)
        os.makedirs(os.path.dirname(abs_output), exist_ok=True)
        expected_duration = timeline.duration

        if expected_duration <= 0.0:
            raise ValueError("Cannot render an empty timeline (duration is 0s).")

        # 1. Optionally compile & save native .kdenlive project file
        kdenlive_path = None
        if export_kdenlive:
            kdenlive_path = os.path.splitext(abs_output)[0] + ".kdenlive"
            KdenliveSerializer.save_to_file(timeline, kdenlive_path)

        # 2. Render execution
        start_time = time.time()
        rendered_with = "ffmpeg"

        # Check if melt is requested and available
        if self.melt_path and os.path.exists(self.melt_path) and kdenlive_path:
            cmd = [
                self.melt_path,
                "-progress", kdenlive_path,
                "-consumer", f"avformat:{abs_output}",
                "vcodec=libx264", "crf=20",
                "acodec=aac", "ab=192k"
            ]
            rendered_with = "melt"
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                # Fall back to FFmpeg if melt failed
                rendered_with = "ffmpeg_fallback"
                cmd = FFmpegCompiler.build_command(timeline, abs_output, use_nvenc=use_nvenc)
                subprocess.run(cmd, check=True, capture_output=True)
        else:
            # Native FFmpeg compiler (primary / standalone)
            cmd = FFmpegCompiler.build_command(timeline, abs_output, use_nvenc=use_nvenc)
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"FFmpeg render failed:\n{res.stderr}")

        render_duration = time.time() - start_time

        # 3. Post-render integrity verification gate
        ok, msg = RenderValidator.verify(abs_output, expected_duration)
        if not ok:
            raise RuntimeError(f"Render output validation failed: {msg}")

        return {
            "status": "success",
            "output_path": abs_output,
            "kdenlive_path": kdenlive_path,
            "rendered_with": rendered_with,
            "expected_duration": expected_duration,
            "render_time_seconds": round(render_duration, 2),
            "file_size_bytes": os.path.getsize(abs_output),
            "verification": msg
        }

