"""
AgentCut Intelligence: Staged Master Pipeline Orchestrator
Spec reference: docs/specs/video-intelligence/spec.md
ADR reference: docs/architecture/architecture-decisions.md (ADR-003, ADR-004, ADR-005)
"""

import os
import json
import time
import subprocess
from dataclasses import asdict
from typing import Dict, Any, Optional, List

from agentcut.intelligence.audio import AudioProcessor
from agentcut.intelligence.vad import VoiceActivityDetector
from agentcut.intelligence.transcribe import TranscriptionEngine
from agentcut.intelligence.disfluency import DisfluencyDetector
from agentcut.intelligence.scene import SceneDetector
from agentcut.intelligence.ocr import OCREngine
from agentcut.intelligence.diarization import SpeakerDiarizer
from agentcut.intelligence.vision_adapter import VisionIntelligenceAdapter
from agentcut.intelligence.proxy import ProxyGenerator
from agentcut.intelligence.chunker import LongVideoChunker

class VideoIntelligencePipeline:
    """
    Orchestrates staged multimodal video analysis adhering to strict sequential memory limits.
    Produces an exhaustive semantic knowledge graph including VAD, transcription,
    disfluencies, scene cuts, OCR, speaker diarization, visual scene descriptions,
    and fast-scrub UI proxy assets.
    """

    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = os.path.abspath(cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)

    def analyze(
        self,
        video_path: str,
        media_id: str = "media_default",
        generate_proxies: bool = False
    ) -> Dict[str, Any]:
        abs_video = os.path.abspath(video_path)
        if not os.path.exists(abs_video):
            raise FileNotFoundError(f"Video file not found: {abs_video}")

        media_cache = os.path.join(self.cache_dir, media_id)
        os.makedirs(media_cache, exist_ok=True)
        keyframes_cache = os.path.join(media_cache, "keyframes")
        thumbs_cache = os.path.join(media_cache, "thumbnails")

        # 0. Metadata Extraction via ffprobe
        meta = self._probe_media(abs_video)

        # 1. Fast-Scrub Proxy & Thumbnail Generation
        proxy_path = None
        thumbnails = []
        if generate_proxies:
            proxy_path = os.path.join(media_cache, "proxy_360p.mp4")
            try:
                ProxyGenerator.generate_proxy_video(abs_video, proxy_path, target_height=360)
            except Exception:
                proxy_path = None

            try:
                thumbnails = ProxyGenerator.generate_thumbnail_strip(
                    abs_video,
                    thumbs_cache,
                    interval_sec=2.0
                )
            except Exception:
                thumbnails = []

        # 2. Audio Extraction & Peak Waveform
        wav_path = os.path.join(media_cache, "audio_16k_mono.wav")
        AudioProcessor.extract_audio_16k_mono(abs_video, wav_path)
        waveform_peaks = AudioProcessor.generate_waveform_peaks(wav_path, points_per_second=50)

        # 3. Voice Activity Detection & Acoustic Pause Categorization
        vad = VoiceActivityDetector()
        speech_segs, silence_segs = vad.analyze_audio(wav_path)

        # 4. Speech-to-Text Transcription (faster-whisper)
        stt = TranscriptionEngine(model_size="tiny")
        sentences, lang, lang_prob = stt.transcribe(wav_path)

        # 5. Speaker Diarization
        speech_intervals = [{"start": s.start, "end": s.end} for s in speech_segs]
        diarizer = SpeakerDiarizer()
        diarization_segments = diarizer.diarize(wav_path, speech_intervals=speech_intervals)

        # Associate speaker tags to word tokens and sentences
        all_words = []
        for s in sentences:
            all_words.extend([asdict(w) for w in s.words])
        SpeakerDiarizer.assign_speakers_to_words(all_words, diarization_segments)

        # 6. Disfluency & Filler Word Detection
        disfluency_detector = DisfluencyDetector(language=lang)
        disfluencies = disfluency_detector.analyze(sentences)

        # 7. Scene Boundary Detection & Keyframes
        scene_detector = SceneDetector(threshold=27.0)
        scenes = scene_detector.detect_scenes(abs_video, keyframes_cache)

        # 8. OCR & Temporal Tracking
        keyframe_records = [(s.keyframe_timestamp, s.keyframe_path) for s in scenes]
        ocr_engine = OCREngine()
        detected_text = ocr_engine.detect_on_frames(keyframe_records)

        # 9. Semantic Visual Description & Shot Framing
        vision_adapter = VisionIntelligenceAdapter()
        kf_dicts = [{"keyframe_path": s.keyframe_path, "timestamp": s.keyframe_timestamp, "scene_id": s.scene_id} for s in scenes]
        visual_descriptions = vision_adapter.analyze_keyframes(kf_dicts, [asdict(t) for t in detected_text])

        # Unified Knowledge Graph Normalization
        unified_graph = {
            "media_id": media_id,
            "filename": os.path.basename(abs_video),
            "file_path": abs_video,
            "proxy_path": proxy_path,
            "metadata": meta,
            "waveform_peaks": waveform_peaks,
            "thumbnails": thumbnails,
            "language": {
                "detected": lang,
                "confidence": lang_prob
            },
            "speech_segments": [asdict(s) for s in speech_segs],
            "diarization": [s.to_dict() for s in diarization_segments],
            "sentences": [asdict(s) for s in sentences],
            "words": all_words,
            "silence_segments": [asdict(s) for s in silence_segs],
            "disfluencies": disfluencies,
            "scenes": [asdict(s) for s in scenes],
            "visual_descriptions": [d.to_dict() for d in visual_descriptions],
            "on_screen_text": [asdict(t) for t in detected_text],
            "analyzed_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Cache JSON report
        report_path = os.path.join(media_cache, "intelligence_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(unified_graph, f, indent=2)

        return unified_graph

    def _probe_media(self, video_path: str) -> Dict[str, Any]:
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            video_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            return {"duration": 0.0, "width": 1920, "height": 1080, "fps": 30.0}

        try:
            data = json.loads(res.stdout)
            format_info = data.get("format", {})
            duration = float(format_info.get("duration", 0.0))

            v_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
            width = int(v_stream.get("width", 1920))
            height = int(v_stream.get("height", 1080))

            fps_str = v_stream.get("r_frame_rate", "30/1")
            if "/" in fps_str:
                num, den = fps_str.split("/")
                fps = round(float(num) / max(1.0, float(den)), 2)
            else:
                fps = float(fps_str)

            return {
                "duration": round(duration, 3),
                "width": width,
                "height": height,
                "fps": fps,
                "video_codec": v_stream.get("codec_name", "h264"),
                "bit_rate": int(format_info.get("bit_rate", 0))
            }
        except Exception:
            return {"duration": 0.0, "width": 1920, "height": 1080, "fps": 30.0}
