"""
AgentCut Intelligence: Long Video Chunking & Master Timestamp Alignment
Spec reference: docs/specs/video-intelligence/spec.md (Section 2.3.4)
"""

import os
import subprocess
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Generator, Tuple

@dataclass
class VideoChunk:
    chunk_index: int
    master_start_sec: float
    master_end_sec: float
    overlap_sec: float
    file_path: str

class LongVideoChunker:
    """
    Partitions long video footage into manageable overlapping segments
    and reconciles child intelligence events into continuous master timestamps.
    """

    def __init__(
        self,
        chunk_duration_sec: float = 300.0,  # 5 minutes
        overlap_sec: float = 5.0            # 5 seconds context overlap
    ):
        self.chunk_duration = chunk_duration_sec
        self.overlap = overlap_sec

    def plan_chunks(self, input_video: str, work_dir: str) -> List[VideoChunk]:
        """
        Determines chunk boundaries based on video duration.
        If video <= chunk_duration, returns a single chunk referencing original file.
        """
        if not os.path.exists(input_video):
            raise FileNotFoundError(f"Input video not found: {input_video}")

        os.makedirs(work_dir, exist_ok=True)
        duration = self._get_duration(input_video)

        if duration <= self.chunk_duration + self.overlap:
            return [
                VideoChunk(
                    chunk_index=0,
                    master_start_sec=0.0,
                    master_end_sec=duration,
                    overlap_sec=0.0,
                    file_path=input_video
                )
            ]

        chunks = []
        cur_start = 0.0
        idx = 0

        while cur_start < duration:
            # Chunk end extends by duration + overlap
            cur_end = min(duration, cur_start + self.chunk_duration + self.overlap)
            chunk_filename = f"chunk_{idx:03d}_{int(cur_start)}s_{int(cur_end)}s.mp4"
            chunk_path = os.path.join(work_dir, chunk_filename)

            chunks.append(VideoChunk(
                chunk_index=idx,
                master_start_sec=cur_start,
                master_end_sec=cur_end,
                overlap_sec=self.overlap if cur_start > 0 else 0.0,
                file_path=chunk_path
            ))

            idx += 1
            cur_start += self.chunk_duration
            if cur_start >= duration:
                break

        return chunks

    def extract_chunk(self, input_video: str, chunk: VideoChunk) -> str:
        """
        Extracts the physical media chunk via FFmpeg if not already extracted.
        """
        if chunk.file_path == input_video:
            return input_video

        if os.path.exists(chunk.file_path) and os.path.getsize(chunk.file_path) > 1024:
            return chunk.file_path

        duration = chunk.master_end_sec - chunk.master_start_sec
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(chunk.master_start_sec),
            "-i", input_video,
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-c:a", "aac",
            chunk.file_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg chunk extraction failed:\n{res.stderr}")

        return chunk.file_path

    @staticmethod
    def reassemble_speech_events(
        chunk_speech_results: List[Tuple[VideoChunk, List[Dict[str, Any]]]]
    ) -> List[Dict[str, Any]]:
        """
        Realigns word-level speech tokens from multiple chunks to master timeline
        and discards redundant tokens in the overlapping margin.
        """
        master_words = []
        last_master_end = -1.0

        for chunk, words in chunk_speech_results:
            offset = chunk.master_start_sec
            for w in words:
                w_start = round(w["start"] + offset, 3)
                w_end = round(w["end"] + offset, 3)

                # If word falls within overlapping region that was already covered, skip
                if w_start < last_master_end - 0.05:
                    continue

                token = dict(w)
                token["start"] = w_start
                token["end"] = w_end
                master_words.append(token)
                last_master_end = max(last_master_end, w_end)

        # Re-number word IDs
        for idx, w in enumerate(master_words):
            w["word_id"] = f"w_{idx+1:04d}"

        return master_words

    @staticmethod
    def reassemble_scenes(
        chunk_scene_results: List[Tuple[VideoChunk, List[Dict[str, Any]]]]
    ) -> List[Dict[str, Any]]:
        """
        Reassembles scene records onto master timestamps.
        """
        master_scenes = []
        last_cut = -1.0

        for chunk, scenes in chunk_scene_results:
            offset = chunk.master_start_sec
            for sc in scenes:
                m_cut = round(sc.get("cut_time", 0.0) + offset, 3)
                m_start = round(sc.get("start_time", 0.0) + offset, 3)
                m_end = round(sc.get("end_time", 0.0) + offset, 3)

                if m_cut < last_cut + 0.5:
                    continue

                sc_copy = dict(sc)
                sc_copy["cut_time"] = m_cut
                sc_copy["start_time"] = m_start
                sc_copy["end_time"] = m_end
                master_scenes.append(sc_copy)
                last_cut = m_cut

        for idx, sc in enumerate(master_scenes):
            sc["scene_id"] = f"scene_{idx+1:03d}"

        return master_scenes

    def _get_duration(self, video_path: str) -> float:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return float(res.stdout.strip()) if res.stdout.strip() else 0.0

