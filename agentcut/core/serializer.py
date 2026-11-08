"""
AgentCut Core: Kdenlive / MLT XML Project Serializer
Spec reference: docs/specs/timeline-editor/spec.md
ADR reference: docs/architecture/architecture-decisions.md (ADR-001, ADR-009)
"""

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict
from agentcut.core.timeline import ProjectTimeline

class KdenliveSerializer:
    """Serializes a Canonical ProjectTimeline into native .kdenlive (MLT XML) format."""

    @staticmethod
    def to_mlt_xml(timeline: ProjectTimeline, pretty: bool = True) -> str:
        root = ET.Element("mlt", LC_NUMERIC="C", version="7.24.0", title=timeline.name)
        
        # Profile element
        ET.SubElement(root, "profile", {
            "description": f"{timeline.profile.width}x{timeline.profile.height} {timeline.profile.fps}fps",
            "width": str(timeline.profile.width),
            "height": str(timeline.profile.height),
            "progressive": "1",
            "sample_aspect_num": "1",
            "sample_aspect_den": "1",
            "display_aspect_num": "16" if timeline.profile.aspect_ratio == "16:9" else "9",
            "display_aspect_den": "9" if timeline.profile.aspect_ratio == "16:9" else "16",
            "frame_rate_num": str(int(timeline.profile.fps)),
            "frame_rate_den": "1",
            "colorspace": "709"
        })

        # Producers (Source Media Pool)
        producers: Dict[str, str] = {}
        for track in timeline.tracks:
            for clip in track.clips:
                abs_path = os.path.abspath(clip.asset_path)
                if abs_path not in producers:
                    prod_id = f"producer_{len(producers)}"
                    producers[abs_path] = prod_id
                    p = ET.SubElement(root, "producer", id=prod_id)
                    ET.SubElement(p, "property", name="resource").text = abs_path
                    ET.SubElement(p, "property", name="kdenlive:clipname").text = os.path.basename(clip.asset_path)
                    ET.SubElement(p, "property", name="kdenlive:id").text = clip.asset_id

        # Maintractor element
        maintractor = ET.SubElement(root, "tractor", id="maintractor")

        # Track Playlists
        fps = timeline.profile.fps
        for track in timeline.tracks:
            playlist_id = f"playlist_{track.track_id}"
            playlist = ET.SubElement(root, "playlist", id=playlist_id)
            current_time = 0.0

            for clip in track.clips:
                # Add gap (blank) if there is space between clips
                if clip.timeline_in > current_time:
                    gap_frames = int(round((clip.timeline_in - current_time) * fps))
                    if gap_frames > 0:
                        ET.SubElement(playlist, "blank", length=str(gap_frames))

                in_frame = int(round(clip.source_in * fps))
                out_frame = int(round(clip.source_out * fps)) - 1
                prod_id = producers[os.path.abspath(clip.asset_path)]

                entry = ET.SubElement(playlist, "entry", {
                    "producer": prod_id,
                    "in": str(in_frame),
                    "out": str(max(in_frame, out_frame))
                })

                # Scale / punch-in filter
                if clip.scale != 1.0:
                    filt = ET.SubElement(entry, "filter", id=f"filter_punch_{clip.clip_id}")
                    ET.SubElement(filt, "property", name="mlt_service").text = "qtblend"
                    ET.SubElement(filt, "property", name="rect").text = (
                        f"0=0 0 {timeline.profile.width} {timeline.profile.height} {clip.scale}"
                    )

                # Volume filter
                if clip.volume != 1.0:
                    filt_vol = ET.SubElement(entry, "filter", id=f"filter_vol_{clip.clip_id}")
                    ET.SubElement(filt_vol, "property", name="mlt_service").text = "volume"
                    ET.SubElement(filt_vol, "property", name="level").text = str(clip.volume)

                current_time = clip.timeline_out

            ET.SubElement(maintractor, "track", producer=playlist_id)

        # Transitions
        for trans in timeline.transitions:
            t_elem = ET.SubElement(maintractor, "transition", id=trans.transition_id)
            service_name = "frei0r.cairoblend" if trans.transition_type == "crossfade" else "composite"
            ET.SubElement(t_elem, "property", name="mlt_service").text = service_name
            ET.SubElement(t_elem, "property", name="in").text = str(int(round(trans.timeline_in * fps)))
            ET.SubElement(t_elem, "property", name="out").text = str(int(round((trans.timeline_in + trans.duration) * fps)))
            ET.SubElement(t_elem, "property", name="a_track").text = str(trans.track_from_index)
            ET.SubElement(t_elem, "property", name="b_track").text = str(trans.track_to_index)

        raw_xml = ET.tostring(root, encoding="utf-8")
        if pretty:
            reparsed = minidom.parseString(raw_xml)
            return reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
        return raw_xml.decode("utf-8")

    @staticmethod
    def save_to_file(timeline: ProjectTimeline, file_path: str) -> str:
        xml_content = KdenliveSerializer.to_mlt_xml(timeline)
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        return file_path

