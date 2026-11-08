"""
AgentCut Core: Canonical Typed Timeline Data Model & Invariants
Spec reference: docs/specs/timeline-editor/spec.md
ADR reference: docs/architecture/architecture-decisions.md (ADR-009)
"""

import json
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class ClipModel:
    clip_id: str
    asset_id: str
    asset_path: str
    timeline_in: float      # Start time on master timeline in seconds
    timeline_out: float     # End time on master timeline in seconds
    source_in: float        # Start time in source footage in seconds
    source_out: float       # End time in source footage in seconds
    speed: float = 1.0
    volume: float = 1.0
    scale: float = 1.0      # 1.0 = normal, 1.15 = dynamic punch-in
    opacity: float = 1.0
    filters: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return self.timeline_out - self.timeline_in

    def validate(self):
        assert self.timeline_out > self.timeline_in, f"Invalid timeline range: {self.timeline_in} -> {self.timeline_out}"
        assert self.source_out > self.source_in, f"Invalid source range: {self.source_in} -> {self.source_out}"
        assert self.speed > 0, "Speed must be strictly positive"

@dataclass
class TextCaptionModel:
    caption_id: str
    text: str
    timeline_in: float
    timeline_out: float
    font_size: int = 42
    font_color: str = "#FED330"    # High-contrast vibrant yellow
    bg_color: str = "#00000088"     # Semi-transparent dark box
    active_word: Optional[str] = None
    highlight_color: str = "#00D9FF"# Electric cyan

    @property
    def duration(self) -> float:
        return self.timeline_out - self.timeline_in

@dataclass
class TransitionModel:
    transition_id: str
    transition_type: str            # 'crossfade', 'wipe', 'luma'
    track_from_index: int
    track_to_index: int
    timeline_in: float
    duration: float

@dataclass
class TrackModel:
    track_id: str
    track_index: int
    track_type: str                 # 'video', 'audio', 'caption'
    name: str
    is_muted: bool = False
    is_locked: bool = False
    clips: List[ClipModel] = field(default_factory=list)

    def sort_clips(self):
        self.clips.sort(key=lambda c: c.timeline_in)

@dataclass
class ProjectProfile:
    width: int = 1920
    height: int = 1080
    fps: float = 30.0
    aspect_ratio: str = "16:9"

@dataclass
class ProjectTimeline:
    project_id: str
    name: str
    profile: ProjectProfile = field(default_factory=ProjectProfile)
    tracks: List[TrackModel] = field(default_factory=list)
    captions: List[TextCaptionModel] = field(default_factory=list)
    transitions: List[TransitionModel] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        max_t = 0.0
        for track in self.tracks:
            for clip in track.clips:
                if clip.timeline_out > max_t:
                    max_t = clip.timeline_out
        for cap in self.captions:
            if cap.timeline_out > max_t:
                max_t = cap.timeline_out
        return max_t

    def get_track(self, track_index: int) -> Optional[TrackModel]:
        for t in self.tracks:
            if t.track_index == track_index:
                return t
        return None

    def ensure_track(self, track_index: int, track_type: str, name: str) -> TrackModel:
        t = self.get_track(track_index)
        if not t:
            t = TrackModel(
                track_id=f"track_{track_type}_{track_index}",
                track_index=track_index,
                track_type=track_type,
                name=name
            )
            self.tracks.append(t)
            self.tracks.sort(key=lambda x: x.track_index)
        return t

    def add_clip(self, track_index: int, clip: ClipModel):
        clip.validate()
        track = self.get_track(track_index)
        if not track:
            raise ValueError(f"Track index {track_index} does not exist.")
        track.clips.append(clip)
        track.sort_clips()

    def split_clip(self, clip_id: str, split_at: float) -> tuple[ClipModel, ClipModel]:
        """Slices an existing clip at master timeline timestamp into two non-destructive halves."""
        target_track = None
        target_clip = None
        for t in self.tracks:
            for c in t.clips:
                if c.clip_id == clip_id:
                    target_track = t
                    target_clip = c
                    break
            if target_clip:
                break

        if not target_clip:
            raise KeyError(f"Clip '{clip_id}' not found on any track.")

        if not (target_clip.timeline_in < split_at < target_clip.timeline_out):
            raise ValueError(f"Split point {split_at} is out of bounds for clip [{target_clip.timeline_in}, {target_clip.timeline_out}].")

        delta = split_at - target_clip.timeline_in
        source_split = target_clip.source_in + (delta * target_clip.speed)

        # Left half
        left_clip = ClipModel(
            clip_id=f"{target_clip.clip_id}_a",
            asset_id=target_clip.asset_id,
            asset_path=target_clip.asset_path,
            timeline_in=target_clip.timeline_in,
            timeline_out=split_at,
            source_in=target_clip.source_in,
            source_out=source_split,
            speed=target_clip.speed,
            volume=target_clip.volume,
            scale=target_clip.scale
        )

        # Right half
        right_clip = ClipModel(
            clip_id=f"{target_clip.clip_id}_b",
            asset_id=target_clip.asset_id,
            asset_path=target_clip.asset_path,
            timeline_in=split_at,
            timeline_out=target_clip.timeline_out,
            source_in=source_split,
            source_out=target_clip.source_out,
            speed=target_clip.speed,
            volume=target_clip.volume,
            scale=target_clip.scale
        )

        # Replace in track
        idx = target_track.clips.index(target_clip)
        target_track.clips[idx] = left_clip
        target_track.clips.insert(idx + 1, right_clip)
        return left_clip, right_clip

    def trim_clip(self, clip_id: str, new_timeline_in: Optional[float] = None, new_timeline_out: Optional[float] = None):
        """Trims virtual in/out points while adjusting source bounds accordingly."""
        for t in self.tracks:
            for c in t.clips:
                if c.clip_id == clip_id:
                    if new_timeline_in is not None:
                        delta = new_timeline_in - c.timeline_in
                        c.source_in += delta * c.speed
                        c.timeline_in = new_timeline_in
                    if new_timeline_out is not None:
                        delta = c.timeline_out - new_timeline_out
                        c.source_out -= delta * c.speed
                        c.timeline_out = new_timeline_out
                    c.validate()
                    t.sort_clips()
                    return c
        raise KeyError(f"Clip '{clip_id}' not found.")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectTimeline":
        tracks_data = data.get("tracks", [])
        captions_data = data.get("captions", [])
        trans_data = data.get("transitions", [])
        prof_data = data.get("profile", {})

        profile = ProjectProfile(**prof_data)
        tracks = []
        for td in tracks_data:
            clips = [ClipModel(**cd) for cd in td.get("clips", [])]
            td_copy = dict(td)
            td_copy["clips"] = clips
            tracks.append(TrackModel(**td_copy))

        captions = [TextCaptionModel(**cd) for cd in captions_data]
        transitions = [TransitionModel(**td) for td in trans_data]

        return cls(
            project_id=data["project_id"],
            name=data["name"],
            profile=profile,
            tracks=tracks,
            captions=captions,
            transitions=transitions,
            metadata=data.get("metadata", {})
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "ProjectTimeline":
        return cls.from_dict(json.loads(json_str))

