# Specification: Video Intelligence Engine

## 1. Module Overview

The **Video Intelligence Engine (VIE)** is the cognitive foundation of AgentCut. Its mission is to transform unedited, raw video and audio streams into a rich, frame-accurate, timestamped semantic knowledge graph before any editing decisions occur.

The VIE eliminates blind cutting. It provides editing agents and human creators with exhaustive multi-modal understanding: who is speaking, what is said word-for-word, where natural conversational pauses occur versus awkward dead air, where visual scene changes happen, what text appears on screen and for how long, and what visual events are depicted.

---

## 2. Requirements & Capabilities

### 2.1 Audio Intelligence
1. **Voice Activity Detection (VAD)**:
   - Millisecond-precise segmentation of speech vs. silence using `Silero VAD`.
   - Window size: 30ms with 512-sample hops at 16kHz.
2. **Acoustic Pause Classification**:
   - **Micro-pause (`< 0.4s`)**: Natural cadence between words; never cut.
   - **Conversational pause (`0.4s - 0.8s`)**: Standard turn-taking or sentence pause; preserved unless tightening pace.
   - **Dramatic pause (`0.8s - 1.5s`)**: Emotionally significant or emphasis pause (detected by preceding speech velocity and pitch descent); preserved intentionally.
   - **Dead silence (`> 1.5s`)**: Unintentional delay, hesitations, or dead air; prime candidate for trimming.
   - **Acoustic Background**: Identification of non-speech audio (background noise, music).
3. **Speech-to-Text Transcription**:
   - Engine: `faster-whisper` using CTranslate2 CUDA FP16/INT8.
   - Word-level timestamps with start, end, and confidence scores `[0.0 - 1.0]`.
   - Multilingual support with automated language identification, with specialized optimization for English and Spanish.
4. **Linguistic Disfluency & Speech Defect Analysis**:
   - **Filler-Word Detection**: Rule-based and token-matching engine identifying fillers:
     - English: *"um", "uh", "uh-huh", "like", "you know", "sort of", "kind of", "I mean", "basically", "literally"*.
     - Spanish: *"este", "bueno", "o sea", "eh", "em", "sabes", "entonces", "tipo"*.
   - **Repetition Detection**: Identifies immediately repeated words or phrases within a 3.0s window (e.g., *"we have to... we have to look"*).
   - **False-Start & Hesitation Detection**: Identifies truncated words and abandoned sentences followed by speech restarts.
5. **Speaker Diarization**:
   - Identifies recording-specific speakers (`speaker_0`, `speaker_1`, etc.) with start and end bounds.
   - Segments are linked to word-level tokens.

### 2.2 Visual Intelligence
1. **Scene Boundary Detection**:
   - Powered by `PySceneDetect` with content-aware adaptive thresholding (`ContentDetector` / `AdaptiveDetector`).
   - Identifies cut points, wipes, and camera transitions.
2. **Adaptive Keyframe Sampler**:
   - Samples frames strategically rather than sending every frame to vision models:
     - Cut boundaries: Frame at `cut_start + 0.1s` and `cut_end - 0.1s`.
     - Motion peaks: Frames with highest inter-frame luminance standard deviation.
     - Baseline: 1 frame every 2.0s for continuous coverage.
3. **On-Screen Text Recognition (OCR)**:
   - Engine: `RapidOCR` (PP-OCRv4 ONNX).
   - Extracts detected text string, confidence score, and normalized bounding box coordinates `[x1, y1, x2, y2]`.
4. **Temporal Text Box Tracking (Deduplication)**:
   - Tracks text boxes across sampled frames.
   - Compares consecutive detections via spatial IoU (threshold: > 0.6) and Levenshtein string similarity (threshold: > 0.8).
   - Consolidates frame-by-frame detections into a single continuous event: `start_time`, `end_time`, `text`, `bounding_box`.
5. **Semantic Visual Description**:
   - Generates concise descriptions of visual actions and framing (e.g., *"Close-up portrait of speaker in studio lighting"*, *"Screen capture of code editor"*, *"Wide angle landscape shot"*).
   - Supported locally via quantized `Qwen2.5-VL-3B` or via pluggable cloud vision API adapter.

### 2.3 Media Preprocessing
1. **Metadata Ingestion**: FFprobe extraction of container metadata (duration, width, height, aspect ratio, frame rate, audio sample rate, channels, bit rate, codecs).
2. **Audio Track Separation**: Converts primary audio to 16kHz mono 16-bit PCM WAV for intelligence pipelines and 48kHz stereo for playback.
3. **Waveform Peak Pre-computation**: Downsamples audio into 100-points-per-second normalized peak pairs `[min, max]` stored as binary floats for instant rendering in UI.
4. **Chunked Pipeline Processing**: Long footage (> 10 mins) is segmented into 5-minute chunks with 5-second overlapping context windows. Master timestamps are preserved continuously without drift.

---

## 3. Data Contract & Unified Schema

All intelligence results are serialized into a validated Pydantic model and SQLite relational tables:

```json
{
  "media_id": "med_101",
  "filename": "raw_interview.mp4",
  "duration": 74.25,
  "fps": 30.0,
  "resolution": "1920x1080",
  "language": "en",
  "speech": [
    {
      "word_id": "w_001",
      "text": "Welcome",
      "start": 0.52,
      "end": 0.98,
      "confidence": 0.99,
      "speaker": "speaker_0",
      "is_filler": false,
      "sentence_id": "s_01"
    },
    {
      "word_id": "w_002",
      "text": "um",
      "start": 1.05,
      "end": 1.35,
      "confidence": 0.94,
      "speaker": "speaker_0",
      "is_filler": true,
      "sentence_id": "s_01"
    }
  ],
  "sentences": [
    {
      "sentence_id": "s_01",
      "text": "Welcome um to today's deep dive into video editing.",
      "start": 0.52,
      "end": 4.10,
      "speaker": "speaker_0"
    }
  ],
  "silences": [
    {
      "silence_id": "sil_01",
      "start": 4.12,
      "end": 6.30,
      "duration": 2.18,
      "category": "dead_silence",
      "recommended_action": "cut"
    },
    {
      "silence_id": "sil_02",
      "start": 12.40,
      "end": 13.20,
      "duration": 0.80,
      "category": "dramatic_pause",
      "recommended_action": "preserve"
    }
  ],
  "disfluencies": [
    {
      "type": "repetition",
      "text": "we decided we decided",
      "start": 18.20,
      "end": 20.10,
      "recommended_cut": [18.20, 19.15]
    }
  ],
  "scenes": [
    {
      "scene_id": "sc_01",
      "start": 0.0,
      "end": 15.4,
      "keyframe_timestamp": 7.2,
      "keyframe_path": "cache/keyframes/kf_sc_01.jpg",
      "description": "Medium close-up of host in front of dark acoustic panel background."
    }
  ],
  "on_screen_text": [
    {
      "text_id": "txt_01",
      "text": "3 RULES OF COMPOSITION",
      "start": 14.5,
      "end": 19.2,
      "confidence": 0.97,
      "bounding_box": [120, 840, 680, 910]
    }
  ]
}
```

---

## 4. Dependencies & Hardware Strategy

- **Target Device**: NVIDIA RTX 4050 Laptop GPU (6GB VRAM, CUDA 13.4).
- **VRAM Lifecycle Execution**:
  1. Initialize `VRAMLifecycleManager`.
  2. Load `faster-whisper` (1.5 GB VRAM) -> Process audio -> Unload model & run `torch.cuda.empty_cache()`.
  3. Load `pyannote.audio` (1.6 GB VRAM) -> Diarize -> Unload model & flush cache.
  4. Run `PySceneDetect` on CPU (0 MB VRAM).
  5. Run `RapidOCR` ONNX on keyframes (~400 MB).
  6. (Optional) Load quantized `Qwen2.5-VL-3B` (2.4 GB VRAM) on selected keyframes -> Unload model.
- **Failover / Fallback**:
  - If CUDA is unavailable or VRAM is below 2GB, the pipeline seamlessly switches to `CPU` mode with quantized models (e.g., CTranslate2 INT8 on CPU), logging an informational warning without interrupting the user.

