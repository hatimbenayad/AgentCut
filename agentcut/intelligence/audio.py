"""
AgentCut Intelligence: Audio Extraction & Peak Waveform Generator
Spec reference: docs/specs/video-intelligence/spec.md
"""

import os
import subprocess
import numpy as np
import wave
from typing import List, Tuple

class AudioProcessor:
    """Handles audio extraction, sample rate conversion, and peak waveform generation."""

    @staticmethod
    def extract_audio_16k_mono(video_path: str, output_wav: str) -> str:
        """Extracts 16kHz mono 16-bit PCM WAV for speech intelligence pipelines."""
        os.makedirs(os.path.dirname(os.path.abspath(output_wav)), exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            output_wav
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg audio extraction failed:\n{res.stderr}")
        return output_wav

    @staticmethod
    def generate_waveform_peaks(wav_path: str, points_per_second: int = 50) -> List[float]:
        """Generates downsampled peak values normalized to [0.0, 1.0] for responsive UI rendering."""
        if not os.path.exists(wav_path):
            raise FileNotFoundError(f"Audio file not found: {wav_path}")

        with wave.open(wav_path, "rb") as wf:
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            audio_bytes = wf.readframes(n_frames)

        samples = np.frombuffer(audio_bytes, dtype=np.int16)
        if len(samples) == 0:
            return []

        # Calculate chunk size per sample point
        samples_per_point = max(1, int(framerate / points_per_second))
        num_points = int(len(samples) / samples_per_point)

        peaks = []
        for i in range(num_points):
            chunk = samples[i * samples_per_point : (i + 1) * samples_per_point]
            if len(chunk) > 0:
                peak = float(np.max(np.abs(chunk))) / 32768.0
                peaks.append(round(peak, 3))
            else:
                peaks.append(0.0)

        return peaks

