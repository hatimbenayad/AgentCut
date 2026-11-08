"""
AgentCut Intelligence: Voice Activity Detection & Acoustic Pause Taxonomy
Spec reference: docs/specs/video-intelligence/spec.md
"""

import wave
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class SpeechSegment:
    start: float
    end: float
    confidence: float

@dataclass
class SilenceSegment:
    start: float
    end: float
    duration: float
    category: str           # 'micro_pause', 'conversational_pause', 'dramatic_pause', 'dead_silence'
    recommended_action: str # 'preserve' or 'cut'

class VoiceActivityDetector:
    """Calibrated Voice Activity Detection and Acoustic Pause Classifier."""

    def __init__(self, frame_duration_ms: int = 30, energy_threshold_ratio: float = 0.05):
        self.frame_duration_ms = frame_duration_ms
        self.energy_threshold_ratio = energy_threshold_ratio

    def analyze_audio(self, wav_16k_mono_path: str) -> tuple[List[SpeechSegment], List[SilenceSegment]]:
        with wave.open(wav_16k_mono_path, "rb") as wf:
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            total_duration = n_frames / float(framerate)
            audio_bytes = wf.readframes(n_frames)

        samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        frame_size = int(framerate * (self.frame_duration_ms / 1000.0))
        n_chunks = len(samples) // frame_size

        if n_chunks == 0:
            return [], []

        # Compute Root Mean Square (RMS) energy per frame
        energies = []
        for i in range(n_chunks):
            frame = samples[i * frame_size : (i + 1) * frame_size]
            rms = np.sqrt(np.mean(frame**2))
            energies.append(rms)

        max_energy = np.max(energies) if len(energies) > 0 else 1.0
        # Dynamic noise floor estimation: 10th percentile
        noise_floor = np.percentile(energies, 15) if len(energies) > 0 else 0.01
        threshold = max(noise_floor * 1.5, max_energy * self.energy_threshold_ratio)

        # Binary speech state per frame
        is_speech = [1 if e > threshold else 0 for e in energies]

        # Smooth binary speech frames (hangover smoothing: bridge micro gaps < 120ms)
        hangover_frames = int(120 / self.frame_duration_ms)
        smoothed = list(is_speech)
        gap = 0
        for i in range(len(smoothed)):
            if smoothed[i] == 0:
                gap += 1
            else:
                if 0 < gap <= hangover_frames and i - gap - 1 >= 0:
                    for j in range(i - gap, i):
                        smoothed[j] = 1
                gap = 0

        # Extract contiguous speech intervals
        speech_segments: List[SpeechSegment] = []
        in_speech = False
        start_frame = 0

        for i, val in enumerate(smoothed):
            if val == 1 and not in_speech:
                in_speech = True
                start_frame = i
            elif val == 0 and in_speech:
                in_speech = False
                t_start = round(start_frame * (self.frame_duration_ms / 1000.0), 3)
                t_end = round(i * (self.frame_duration_ms / 1000.0), 3)
                if t_end - t_start >= 0.1:  # Filter blips < 100ms
                    speech_segments.append(SpeechSegment(t_start, t_end, 0.95))

        if in_speech:
            t_start = round(start_frame * (self.frame_duration_ms / 1000.0), 3)
            speech_segments.append(SpeechSegment(t_start, round(total_duration, 3), 0.95))

        # Compute Complementary Silence Segments
        silence_segments: List[SilenceSegment] = []
        current_t = 0.0

        for seg in speech_segments:
            if seg.start > current_t:
                duration = round(seg.start - current_t, 3)
                if duration >= 0.15:  # Only evaluate pauses >= 150ms
                    category, action = self._classify_pause(duration)
                    silence_segments.append(SilenceSegment(
                        start=round(current_t, 3),
                        end=round(seg.start, 3),
                        duration=duration,
                        category=category,
                        recommended_action=action
                    ))
            current_t = seg.end

        if current_t < total_duration:
            duration = round(total_duration - current_t, 3)
            if duration >= 0.15:
                category, action = self._classify_pause(duration)
                silence_segments.append(SilenceSegment(
                    start=round(current_t, 3),
                    end=round(total_duration, 3),
                    duration=duration,
                    category=category,
                    recommended_action=action
                ))

        return speech_segments, silence_segments

    def _classify_pause(self, duration: float) -> tuple[str, str]:
        """Classifies pauses into the 4-tier taxonomy."""
        if duration < 0.4:
            return "micro_pause", "preserve"
        elif duration < 0.8:
            return "conversational_pause", "preserve"
        elif duration < 1.5:
            return "dramatic_pause", "preserve"
        else:
            return "dead_silence", "cut"
