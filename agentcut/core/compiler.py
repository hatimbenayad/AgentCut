"""
AgentCut Core: Native FFmpeg Filtergraph Compiler & Render Dispatcher
Spec reference: docs/specs/rendering/spec.md
ADR reference: docs/architecture/architecture-decisions.md (ADR-002, ADR-009)
"""

import os
import subprocess
from typing import List, Dict, Any, Optional
from agentcut.core.timeline import ProjectTimeline

class FFmpegCompiler:
    """Compiles a Canonical ProjectTimeline into an optimized FFmpeg filtergraph pipeline."""

    @staticmethod
    def build_command(
        timeline: ProjectTimeline,
        output_mp4: str,
        target_width: Optional[int] = None,
        target_height: Optional[int] = None,
        use_nvenc: bool = False
    ) -> List[str]:
        width = target_width or timeline.profile.width
        height = target_height or timeline.profile.height
        
        cmd = ["ffmpeg", "-y"]

        # Collect unique media inputs
        input_map: Dict[str, int] = {}
        for track in timeline.tracks:
            for clip in track.clips:
                abs_path = os.path.abspath(clip.asset_path)
                if abs_path not in input_map:
                    input_map[abs_path] = len(input_map)
                    cmd.extend(["-i", abs_path])

        if not input_map:
            raise ValueError("Timeline contains no media clips to render.")

        filter_chains: List[str] = []
        v_segments: List[str] = []
        a_segments: List[str] = []

        # Process Primary Video Track
        v_track = next((t for t in timeline.tracks if t.track_type == "video"), None)
        if v_track and v_track.clips:
            for idx, clip in enumerate(v_track.clips):
                in_idx = input_map[os.path.abspath(clip.asset_path)]
                v_tag = f"v_{idx}"
                a_tag = f"a_{idx}"

                # Video Trim & Aspect/Punch-in Scaling
                v_trim = f"[{in_idx}:v]trim=start={clip.source_in}:end={clip.source_out},setpts=PTS-STARTPTS"
                
                # Check aspect ratio crop (e.g. 9:16 vertical) or punch-in zoom
                if clip.scale != 1.0:
                    sw = int(width / clip.scale)
                    sh = int(height / clip.scale)
                    ox = int((width - sw) / 2)
                    oy = int((height - sh) / 2)
                    v_trim += f",crop={sw}:{sh}:{ox}:{oy},scale={width}:{height},setsar=1"
                else:
                    v_trim += f",scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1"

                v_trim += f"[{v_tag}]"
                filter_chains.append(v_trim)
                v_segments.append(f"[{v_tag}]")

                # Audio Trim & Volume
                a_trim = f"[{in_idx}:a]atrim=start={clip.source_in}:end={clip.source_out},asetpts=PTS-STARTPTS"
                if clip.volume != 1.0:
                    a_trim += f",volume={clip.volume}"
                a_trim += f"[{a_tag}]"
                filter_chains.append(a_trim)
                a_segments.append(f"[{a_tag}]")

        # Interleave video and audio for concat filter
        interleaved: List[str] = []
        for i in range(len(v_segments)):
            interleaved.append(v_segments[i])
            interleaved.append(a_segments[i])

        num_seg = len(v_segments)
        concat_filter = f"{''.join(interleaved)}concat=n={num_seg}:v=1:a=1[v_base][a_base]"
        filter_chains.append(concat_filter)

        # Process Captions Overlay
        v_final = "[v_base]"
        for c_idx, cap in enumerate(timeline.captions):
            out_tag = f"[v_cap_{c_idx}]"
            safe_text = cap.text.replace("'", "").replace(":", "")
            drawtext = (
                f"{v_final}drawtext=text='{safe_text}':"
                f"fontsize={cap.font_size}:fontcolor={cap.font_color}:"
                f"box=1:boxcolor={cap.bg_color}:boxborderw=10:"
                f"x=(w-text_w)/2:y=h-text_h-80:"
                f"enable='between(t,{cap.timeline_in},{cap.timeline_out})'{out_tag}"
            )
            filter_chains.append(drawtext)
            v_final = out_tag

        full_filtergraph = ";".join(filter_chains)
        vcodec = "h264_nvenc" if use_nvenc else "libx264"

        cmd.extend([
            "-filter_complex", full_filtergraph,
            "-map", v_final,
            "-map", "[a_base]",
            "-c:v", vcodec,
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            output_mp4
        ])
        return cmd
