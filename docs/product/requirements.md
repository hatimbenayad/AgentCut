# AgentCut: Comprehensive Requirements Specification

## 1. Requirement Traceability Matrix

Every requirement is assigned a unique identifier (`REQ-xxx`), categorized, prioritized (MoSCoW: Must, Should, Could, Won't), and tracked against its implementation lifecycle status:
- `Not started`
- `Specified`
- `In progress`
- `Implemented`
- `Tested`
- `Verified`

---

## 2. Functional Requirements

### 2.1 Media Management & Preprocessing

| Req ID | Title | Description | Priority | Status |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-MED-01** | Multi-format Media Ingestion | Ingest video (MP4, MOV, MKV, WebM), audio (WAV, MP3, AAC, FLAC), and image (PNG, JPG) assets into the local project media bin. | **Must** | `Specified` |
| **REQ-MED-02** | Metadata Extraction | Extract stream properties (duration, fps, resolution, color space, audio sample rate, channels, codec) via FFprobe. | **Must** | `Specified` |
| **REQ-MED-03** | Audio Extraction & Normalization | Extract high-fidelity 16kHz mono 16-bit PCM WAV for intelligence pipelines and stereo 48kHz for playback/timeline. | **Must** | `Specified` |
| **REQ-MED-04** | Audio Waveform Peaks Generation | Generate downsampled waveform peak datasets (e.g. 100 points/sec) for instant timeline and review visualization without memory bloat. | **Must** | `Specified` |
| **REQ-MED-05** | Thumbnail Grid Generation | Generate temporal thumbnail sprites/strips across the asset for video scrubbing in the media bin and timeline clips. | **Must** | `Specified` |
| **REQ-MED-06** | Chunked Pipeline Processing | Split long media (> 10 minutes) into seamless overlapping processing segments while preserving absolute master timestamps. | **Must** | `Specified` |
| **REQ-MED-07** | Source Media Immutability | Source files are mounted read-only; intermediate proxies and extracted waveforms are isolated in a cache folder. | **Must** | `Specified` |

---

### 2.2 Video Intelligence Engine

| Req ID | Title | Description | Priority | Status |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-INT-01** | Voice Activity Detection (VAD) | Run Silero VAD to segment audio into speech and non-speech regions with millisecond accuracy (< 30ms window). | **Must** | `Specified` |
| **REQ-INT-02** | Acoustic Pause Classification | Categorize non-speech intervals into: (a) micro-pauses (< 0.4s), (b) conversational pauses (0.4-0.8s), (c) dramatic pauses (0.8-1.5s), and (d) dead silences (> 1.5s). | **Must** | `Specified` |
| **REQ-INT-03** | Speech-to-Text Transcription | Transcribe dialogue using `faster-whisper` (CTranslate2) with language detection, supporting English and Spanish. | **Must** | `Specified` |
| **REQ-INT-04** | Word-Level Timestamps | Compute word start, end, and confidence scores using cross-attention alignment / forced alignment. | **Must** | `Specified` |
| **REQ-INT-05** | Speaker Diarization | Identify speaker turns (`speaker_0`, `speaker_1`) across recordings using pyannote or acoustic clustering. | **Must** | `Specified` |
| **REQ-INT-06** | Speech Disfluency Detection | Detect filler words ("um", "uh", "like", "you know", "este"), repetitions (e.g. "we we decided"), and false starts. | **Must** | `Specified` |
| **REQ-INT-07** | Visual Scene Boundary Detection | Detect hard cuts and transitions using `PySceneDetect` content and threshold algorithms. | **Must** | `Specified` |
| **REQ-INT-08** | Adaptive Keyframe Sampling | Extract representative visual frames at scene heads/tails and high-motion peaks rather than uniform redundant frames. | **Must** | `Specified` |
| **REQ-INT-09** | On-Screen Text Recognition (OCR) | Detect on-screen text using RapidOCR/PaddleOCR with bounding boxes `[x1, y1, x2, y2]`. | **Must** | `Specified` |
| **REQ-INT-10** | Temporal OCR Box Tracking | Group consecutive keyframe OCR detections using IoU and text similarity into persistent temporal intervals `[t_start, t_end]` to eliminate duplicate events. | **Must** | `Specified` |
| **REQ-INT-11** | Semantic Visual Description | Generate scene-level descriptions of visual events ("close-up portrait", "screencast demonstration", "outdoor landscape"). | **Should** | `Specified` |
| **REQ-INT-12** | Unified Intelligence Schema | Consolidate speech, pause, speaker, OCR, scene, and keyframe metadata into a structured, validated SQLite + JSON schema. | **Must** | `Specified` |

---

### 2.3 Analysis Review & Human Correction Interface

| Req ID | Title | Description | Priority | Status |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-REV-01** | Interactive Waveform & Transcript Sync | Clicking any word in the transcript jumps the preview playhead to the exact start timestamp; playing updates the highlighted word in real time. | **Must** | `Specified` |
| **REQ-REV-02** | Visual Silence & Pause Overlays | Display silence regions directly over the audio waveform color-coded by category (green=conversational, orange=dramatic, red=dead silence). | **Must** | `Specified` |
| **REQ-REV-03** | Transcript Text Correction | Enable direct inline editing of transcribed text; edits update the underlying SQLite intelligence store. | **Must** | `Specified` |
| **REQ-REV-04** | Speaker Label Management | Allow re-naming speakers and reassigning speech segments to different speaker tracks. | **Must** | `Specified` |
| **REQ-REV-05** | Scene & Keyframe Inspector | Display extracted scene cuts and keyframe thumbnails with manual add/delete scene boundary capability. | **Must** | `Specified` |

---

### 2.4 Timeline & Editing Engine (Kdenlive & MLT)

| Req ID | Title | Description | Priority | Status |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-EDT-01** | Multitrack Timeline Model | Abstract timeline supporting unlimited video tracks (V1, V2...), audio tracks (A1, A2...), and caption tracks. | **Must** | `Specified` |
| **REQ-EDT-02** | Non-Destructive Clip Operations | Implement `add_clip`, `remove_clip`, `trim_clip`, `split_clip`, `move_clip`, and `duplicate_clip` with source in/out preservation. | **Must** | `Specified` |
| **REQ-EDT-03** | Transitions & Compositing | Support video transitions (crossfade, wipe, composite) and audio crossfades between tracks. | **Must** | `Specified` |
| **REQ-EDT-04** | Effects & Filters | Apply filters including volume adjustment, audio normalization, brightness/contrast, saturation, and transform/zoom. | **Must** | `Specified` |
| **REQ-EDT-05** | Dynamic Jump Cuts & Punch-ins | Support automatic punch-in (1.1x - 1.2x scale centered on speaker) across jump cuts for conversational flow. | **Must** | `Specified` |
| **REQ-EDT-06** | Synchronized Animated Captions | Generate styled captions (font, size, color, background, outline, animated active word highlight) aligned to word timestamps. | **Must** | `Specified` |
| **REQ-EDT-07** | Native Kdenlive XML Serialization | Export the timeline to a valid, well-formed `.kdenlive` (MLT XML) project file readable by desktop Kdenlive 23.x/24.x. | **Must** | `Specified` |
| **REQ-EDT-08** | Transactional Undo/Redo & Snapshots | Maintain an undo/redo stack and automatic checkpoint backups on every state mutation. | **Must** | `Specified` |

---

### 2.5 Model Context Protocol (MCP) Server

| Req ID | Title | Description | Priority | Status |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-MCP-01** | Stdio & SSE Transport Support | Expose the MCP server via standard input/output (stdio) for local CLI agents and SSE/HTTP for network clients. | **Must** | `Specified` |
| **REQ-MCP-02** | Typed Project Tools | Expose `create_project`, `open_project`, `save_project`, `get_project_info`, `get_project_timeline`, `get_project_assets`. | **Must** | `Specified` |
| **REQ-MCP-03** | Typed Intelligence Tools | Expose `analyze_video`, `get_video_analysis`, `get_transcript`, `get_speech_segments`, `get_silence_segments`, `get_speakers`, `get_detected_text`, `get_scene_boundaries`, `search_video_content`. | **Must** | `Specified` |
| **REQ-MCP-04** | Typed Editing Tools | Expose `add_video_clip`, `add_audio_clip`, `remove_clip`, `split_clip`, `trim_clip`, `move_clip`, `duplicate_clip`, `set_clip_speed`, `set_clip_volume`, `set_clip_opacity`. | **Must** | `Specified` |
| **REQ-MCP-05** | Typed Effects & Caption Tools | Expose `add_transition`, `add_video_effect`, `add_audio_effect`, `adjust_color`, `add_text_overlay`, `generate_captions`, `style_captions`. | **Must** | `Specified` |
| **REQ-MCP-06** | Typed Rendering Tools | Expose `generate_preview`, `render_video`, `export_video`, `get_render_status`. | **Must** | `Specified` |
| **REQ-MCP-07** | Agent Collaboration Tools | Expose `register_agent`, `get_agent_status`, `publish_editing_event`, `create_checkpoint`, `undo_last_operation`. | **Must** | `Specified` |
| **REQ-MCP-08** | Concurrency Locking & Validation | Enforce project write locks during mutations, reject invalid in/out bounds, and return structured JSON error payloads. | **Must** | `Specified` |

---

### 2.6 Multi-Agent Orchestration

| Req ID | Title | Description | Priority | Status |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-AGT-01** | Specialized Agent Roles | Support distinct logical roles: Director, Footage Analyst, Video Editor, Audio Engineer, Caption Designer, Colorist, Quality Controller. | **Must** | `Specified` |
| **REQ-AGT-02** | Shared Project State & Event Ledger | All agents coordinate against a single authoritative project state and log operations to an atomic SQLite event ledger. | **Must** | `Specified` |
| **REQ-AGT-03** | Conflict Resolution | Prevent concurrent agents from overlapping edits on identical track intervals through fine-grained track-interval locks. | **Must** | `Specified` |
| **REQ-AGT-04** | Agent Operational Provenance | Every timeline operation records `agent_id`, `agent_name`, `agent_color`, `action_type`, target track, timeline in/out, and human-readable explanation. | **Must** | `Specified` |

---

### 2.7 Signature Feature: Cinematic Multi-Agent Editing Replay

| Req ID | Title | Description | Priority | Status |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-RPL-01** | Visual Event Reconstruction | Reconstruct the entire editing process visually from the immutable event ledger without altering the underlying project. | **Must** | `Specified` |
| **REQ-RPL-02** | Animated Color-Coded Cursors | Render animated cursors for each participating agent (Cyan=Editor, Purple=Audio, Yellow=Captions, Green=Colorist, Red=QC) with name tags. | **Must** | `Specified` |
| **REQ-RPL-03** | Visual Timeline Manipulations | Smoothly animate clips dragging from media bin to timeline tracks, trimming handles, razor blade splits, and popping captions. | **Must** | `Specified` |
| **REQ-RPL-04** | Replay Scrubbing & Speed Control | Playback controls: Play, Pause, Scrubber, Full-screen, Speed presets (0.5x, 1x, 2x, 4x), and instant **Restart Animation** button. | **Must** | `Specified` |
| **REQ-RPL-05** | Deterministic Playback | Replaying the session multiple times yields identical cursor paths and timeline transformations. | **Must** | `Specified` |

---

### 2.8 Rendering & Export

| Req ID | Title | Description | Priority | Status |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-RND-01** | Dual-Engine Renderer | Support headless MLT `melt` command rendering and high-performance FFmpeg filtergraph fallback rendering. | **Must** | `Specified` |
| **REQ-RND-02** | Format & Aspect Ratio Presets | Export to H.264/AAC MP4 across standard resolutions: 1080p, 4K, 16:9 (Landscape), 9:16 (Vertical TikTok/Reels), 1:1 (Square). | **Must** | `Specified` |
| **REQ-RND-03** | Render Progress & Cancellation | Stream real-time percentage progress, elapsed time, ETA, and support immediate cancellation without corrupted files. | **Must** | `Specified` |
| **REQ-RND-04** | Output Verification | Programmatically verify output file integrity (non-zero size, valid header, matching duration within ±0.2s) before reporting success. | **Must** | `Specified` |

---

## 3. Non-Functional Requirements (NFR)

### 3.1 Performance & Hardware Constraints (RTX 4050 6GB VRAM, 24GB RAM)
- **NFR-PERF-01**: **Peak VRAM Cap**: At no time during inference or rendering shall GPU VRAM allocation exceed **4.2 GB** (leaving headroom for Windows DWM and OS processes).
- **NFR-PERF-02**: **Sequential Model Lifecycle**: Heavy neural models (faster-whisper, pyannote, Qwen-VL) must follow strict sequential load-infer-unload lifecycles with explicit CUDA garbage collection.
- **NFR-PERF-03**: **CPU Offloading**: Scene detection (`PySceneDetect`) and waveform generation must execute on CPU/OpenCV using multithreaded worker pools.
- **NFR-PERF-04**: **Replay Performance**: The Cinematic Multi-Agent Replay must maintain a steady **60 FPS** during animation on standard 1080p desktop displays without frame drops.

### 3.2 Security & Reliability
- **NFR-SEC-01**: **Filesystem Sandboxing**: MCP and agent commands are restricted to the project root directory and media cache; arbitrary path traversal or execution is rejected.
- **NFR-SEC-02**: **Original Footage Immutability**: Source media files are flagged read-only and never opened in write mode.
- **NFR-SEC-03**: **Crash Recovery & Auto-Save**: Project state and event ledgers are committed to SQLite with WAL (Write-Ahead Logging) to ensure zero data loss on unexpected power loss or crash.
- **NFR-SEC-04**: **Offline-First Resilience**: All core features (VAD, transcription, editing, rendering, replay) must function completely offline without external cloud dependencies.

