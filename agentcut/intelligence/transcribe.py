"""
AgentCut Intelligence: Speech-to-Text Transcription Engine
Spec reference: docs/specs/video-intelligence/spec.md
ADR reference: docs/architecture/architecture-decisions.md (ADR-003, ADR-013)
"""

import gc
import os
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

@dataclass
class WordToken:
    word: str
    start: float
    end: float
    confidence: float
    is_filler: bool = False

@dataclass
class SentenceSegment:
    sentence_id: str
    text: str
    start: float
    end: float
    words: List[WordToken]

class TranscriptionEngine:
    """Wrapper around faster-whisper supporting word-level timestamps and strict memory cleanup."""

    def __init__(self, model_size: str = "tiny", language: Optional[str] = None):
        self.model_size = model_size
        self.language = language

    def transcribe(self, audio_wav_path: str) -> tuple[List[SentenceSegment], str, float]:
        from faster_whisper import WhisperModel
        import ctranslate2

        # Load model: prioritize local cached files to prevent remote network timeouts
        def _get_model(dev: str, comp: str):
            try:
                return WhisperModel(self.model_size, device=dev, compute_type=comp, cpu_threads=8, local_files_only=True)
            except Exception:
                return WhisperModel(self.model_size, device=dev, compute_type=comp, cpu_threads=8)

        cuda_available = ctranslate2.get_cuda_device_count() > 0
        device = "cuda" if cuda_available else "cpu"
        compute_type = "int8_float16" if cuda_available else "int8"

        try:
            model = _get_model(device, compute_type)
        except Exception:
            device = "cpu"
            compute_type = "int8"
            model = _get_model("cpu", "int8")

        try:
            try:
                segments, info = model.transcribe(
                    audio_wav_path,
                    language=self.language,
                    word_timestamps=True,
                    beam_size=1
                )
                seg_list = list(segments)
            except (RuntimeError, Exception) as err:
                # Fallback to CPU execution if CUDA runtime failure occurs
                model = _get_model("cpu", "int8")
                segments, info = model.transcribe(
                    audio_wav_path,
                    language=self.language,
                    word_timestamps=True,
                    beam_size=1
                )
                seg_list = list(segments)

            sentences: List[SentenceSegment] = []
            for s_idx, seg in enumerate(seg_list):
                words: List[WordToken] = []
                if seg.words:
                    for w in seg.words:
                        clean_word = w.word.strip()
                        words.append(WordToken(
                            word=clean_word,
                            start=round(w.start, 3),
                            end=round(w.end, 3),
                            confidence=round(w.probability, 3)
                        ))

                sentences.append(SentenceSegment(
                    sentence_id=f"sent_{s_idx+1:03d}",
                    text=seg.text.strip(),
                    start=round(seg.start, 3),
                    end=round(seg.end, 3),
                    words=words
                ))

            detected_lang = info.language
            lang_prob = round(info.language_probability, 3)
            return sentences, detected_lang, lang_prob

        finally:
            # Enforce clean memory unload
            del model
            gc.collect()
