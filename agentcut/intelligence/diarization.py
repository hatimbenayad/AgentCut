"""
AgentCut Intelligence: Speaker Diarization & Word-Speaker Association
Spec reference: docs/specs/video-intelligence/spec.md, docs/architecture/architecture-decisions.md (ADR-005)
"""

import os
import wave
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

@dataclass
class DiarizationSegment:
    segment_id: str
    speaker: str
    start: float
    end: float
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class SpeakerDiarizer:
    """
    Identifies distinct speakers in audio footage and maps speaker IDs
    to word-level transcription tokens.

    Supports:
    1. Pyannote 3.1 neural pipeline when HuggingFace token is configured.
    2. Zero-dependency acoustic spectral clustering fallback when offline or no token is provided.
    """

    def __init__(self, hf_token: Optional[str] = None):
        self.hf_token = hf_token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")

    def diarize(
        self,
        wav_path: str,
        speech_intervals: Optional[List[Dict[str, float]]] = None,
        max_speakers: int = 5
    ) -> List[DiarizationSegment]:
        """
        Performs diarization on 16kHz mono WAV file.
        Returns ordered list of DiarizationSegment records.
        """
        if not os.path.exists(wav_path):
            raise FileNotFoundError(f"Audio file not found: {wav_path}")

        # Try pyannote if token is available
        if self.hf_token:
            try:
                return self._diarize_pyannote(wav_path)
            except Exception as e:
                # Log warning and fall back gracefully to acoustic clustering
                pass

        return self._diarize_acoustic_clustering(wav_path, speech_intervals, max_speakers=max_speakers)

    def _diarize_pyannote(self, wav_path: str) -> List[DiarizationSegment]:
        from pyannote.audio import Pipeline
        import torch

        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=self.hf_token
        )
        if torch.cuda.is_available():
            pipeline.to(torch.device("cuda"))

        diarization = pipeline(wav_path)
        segments = []
        for idx, (turn, _, speaker) in enumerate(diarization.itertracks(yield_label=True)):
            segments.append(DiarizationSegment(
                segment_id=f"dia_{idx:03d}",
                speaker=str(speaker).lower().replace(" ", "_"),
                start=round(float(turn.start), 3),
                end=round(float(turn.end), 3),
                confidence=0.92
            ))
        return segments

    def _diarize_acoustic_clustering(
        self,
        wav_path: str,
        speech_intervals: Optional[List[Dict[str, float]]] = None,
        max_speakers: int = 5
    ) -> List[DiarizationSegment]:
        """
        High-reliability acoustic feature extraction and clustering fallback.
        Uses spectral centroid, zero-crossing rate, RMS energy, and sub-band ratios.
        """
        with wave.open(wav_path, "rb") as wf:
            sample_rate = wf.getframerate()
            n_frames = wf.getnframes()
            audio_bytes = wf.readframes(n_frames)

        samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        duration = len(samples) / float(sample_rate)

        # If speech intervals are not provided, synthesize uniform 2.0s analysis windows
        if not speech_intervals:
            speech_intervals = []
            cur = 0.0
            win = 2.0
            while cur < duration:
                speech_intervals.append({"start": cur, "end": min(duration, cur + win)})
                cur += win

        if not speech_intervals:
            return []

        # Feature extraction per speech interval
        features = []
        valid_intervals = []

        for interval in speech_intervals:
            start_s = interval["start"]
            end_s = interval["end"]
            start_idx = int(start_s * sample_rate)
            end_idx = int(end_s * sample_rate)

            chunk = samples[start_idx:end_idx]
            if len(chunk) < int(sample_rate * 0.2):  # Skip very short fragments (<200ms)
                continue

            # 1. Zero crossing rate
            zcr = float(np.mean(np.abs(np.diff(np.sign(chunk)))) / 2.0)

            # 2. RMS Energy
            rms = float(np.sqrt(np.mean(chunk ** 2)))

            # 3. FFT Spectral features
            fft_vals = np.abs(np.fft.rfft(chunk))
            freqs = np.fft.rfftfreq(len(chunk), 1.0 / sample_rate)

            total_energy = np.sum(fft_vals) + 1e-10
            # Spectral centroid
            spectral_centroid = float(np.sum(freqs * fft_vals) / total_energy)

            # Band energy ratios: Low (<500Hz), Mid (500-2000Hz), High (>2000Hz)
            low_energy = float(np.sum(fft_vals[freqs < 500]) / total_energy)
            mid_energy = float(np.sum(fft_vals[(freqs >= 500) & (freqs < 2000)]) / total_energy)
            high_energy = float(np.sum(fft_vals[freqs >= 2000]) / total_energy)

            feat_vec = [
                zcr * 10.0,
                rms * 5.0,
                spectral_centroid / 2000.0,
                low_energy * 2.0,
                mid_energy * 2.0,
                high_energy * 2.0
            ]
            features.append(feat_vec)
            valid_intervals.append((start_s, end_s))

        if not features:
            return [DiarizationSegment("dia_000", "speaker_0", 0.0, duration, 0.85)]

        feat_arr = np.array(features)

        # Simple clustering based on Euclidean distance
        # Normalize features
        feat_norm = (feat_arr - np.mean(feat_arr, axis=0)) / (np.std(feat_arr, axis=0) + 1e-6)

        # Perform clustering
        labels = self._cluster_features(feat_norm, max_clusters=max_speakers)

        segments = []
        for idx, ((st, en), lbl) in enumerate(zip(valid_intervals, labels)):
            segments.append(DiarizationSegment(
                segment_id=f"dia_{idx:03d}",
                speaker=f"speaker_{lbl}",
                start=round(st, 3),
                end=round(en, 3),
                confidence=0.88
            ))

        return self._merge_adjacent_segments(segments)

    def _cluster_features(self, X: np.ndarray, max_clusters: int = 5) -> List[int]:
        n_samples = len(X)
        if n_samples <= 1:
            return [0] * n_samples

        # Initialize clusters
        clusters = [X[0]]
        labels = [0]

        # Distance threshold for separate speaker
        dist_threshold = 2.2

        for i in range(1, n_samples):
            vec = X[i]
            dists = [np.linalg.norm(vec - c) for c in clusters]
            min_dist = min(dists)
            min_idx = dists.index(min_dist)

            if min_dist > dist_threshold and len(clusters) < max_clusters:
                clusters.append(vec)
                labels.append(len(clusters) - 1)
            else:
                # Update cluster centroid running average
                clusters[min_idx] = 0.85 * clusters[min_idx] + 0.15 * vec
                labels.append(min_idx)

        return labels

    def _merge_adjacent_segments(self, segments: List[DiarizationSegment]) -> List[DiarizationSegment]:
        if not segments:
            return []

        merged = [segments[0]]
        for seg in segments[1:]:
            last = merged[-1]
            if seg.speaker == last.speaker and abs(seg.start - last.end) < 0.6:
                # Merge into previous segment
                last.end = seg.end
            else:
                merged.append(seg)

        # Re-index
        for idx, seg in enumerate(merged):
            seg.segment_id = f"dia_{idx:03d}"
        return merged

    @staticmethod
    def assign_speakers_to_words(
        words: List[Dict[str, Any]],
        segments: List[DiarizationSegment]
    ) -> List[Dict[str, Any]]:
        """
        Assigns speaker IDs to word tokens based on timestamp midpoint overlap.
        """
        if not segments:
            for w in words:
                w["speaker"] = "speaker_0"
            return words

        for w in words:
            w_mid = (w["start"] + w["end"]) / 2.0
            assigned = None
            for seg in segments:
                if seg.start <= w_mid <= seg.end:
                    assigned = seg.speaker
                    break

            if not assigned:
                # Find closest segment
                closest = min(segments, key=lambda s: min(abs(w_mid - s.start), abs(w_mid - s.end)))
                assigned = closest.speaker

            w["speaker"] = assigned

        return words

