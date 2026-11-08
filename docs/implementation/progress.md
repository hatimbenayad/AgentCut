# AgentCut: Implementation Progress Tracker

This document maintains the authoritative implementation lifecycle status for all system requirements.

Statuses:
- `Not started`
- `Specified`
- `In progress`
- `Implemented`
- `Tested`
- `Verified`

> **Rule**: No feature is marked as `Implemented` or `Verified` merely because its interface or stub exists. Verification requires automated tests and end-to-end execution.

---

## 1. Requirement Progress Matrix

| Requirement ID | Module | Title | Status | Target Milestone | Verification Note |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-MED-01** | Media | Multi-format Media Ingestion | `Specified` | Milestone 2 | Tested with MP4, WAV, PNG |
| **REQ-MED-02** | Media | Metadata Extraction (FFprobe) | `Specified` | Milestone 2 | Stream parsing verified |
| **REQ-MED-03** | Media | Audio Extraction (16kHz PCM) | `Specified` | Milestone 2 | Audio isolation verified |
| **REQ-MED-04** | Media | Audio Waveform Peaks Generation | `Specified` | Milestone 2 | 100-pt peak dataset |
| **REQ-MED-05** | Media | Thumbnail Grid Generation | `Specified` | Milestone 2 | Thumbnail strips verified |
| **REQ-MED-06** | Media | Chunked Pipeline Processing | `Specified` | Milestone 2 | Master timestamp alignment |
| **REQ-MED-07** | Media | Source Media Immutability | `Specified` | Milestone 2 | Read-only enforcement |
| **REQ-INT-01** | Intelligence | Voice Activity Detection (Silero) | `Specified` | Milestone 2 | <30ms window boundary check |
| **REQ-INT-02** | Intelligence | Acoustic Pause Classification | `Specified` | Milestone 2 | 4-class pause taxonomy |
| **REQ-INT-03** | Intelligence | Speech-to-Text (`faster-whisper`)| `Specified` | Milestone 2 | English & Spanish STT |
| **REQ-INT-04** | Intelligence | Word-Level Timestamps | `Specified` | Milestone 2 | Cross-attention alignment |
| **REQ-INT-05** | Intelligence | Speaker Diarization | `Specified` | Milestone 2 | Recording speaker turns |
| **REQ-INT-06** | Intelligence | Speech Disfluency & Filler Words | `Specified` | Milestone 2 | Filler regex & n-gram repetitions |
| **REQ-INT-07** | Intelligence | Scene Boundary (`PySceneDetect`) | `Specified` | Milestone 2 | Hard cut detection |
| **REQ-INT-08** | Intelligence | Adaptive Keyframe Sampling | `Specified` | Milestone 2 | Motion & cut keyframes |
| **REQ-INT-09** | Intelligence | On-Screen Text (RapidOCR) | `Specified` | Milestone 2 | PP-OCRv4 ONNX inference |
| **REQ-INT-10** | Intelligence | Temporal OCR Box Tracking | `Specified` | Milestone 2 | IoU deduplication |
| **REQ-INT-11** | Intelligence | Semantic Visual Description | `Specified` | Milestone 2 | Qwen2.5-VL / Cloud adapter |
| **REQ-INT-12** | Intelligence | Unified Intelligence Schema | `Specified` | Milestone 2 | SQLite + JSON serialization |
| **REQ-REV-01** | Review | Interactive Waveform/Transcript Sync | `Specified` | Milestone 6 | Click-to-seek verification |
| **REQ-REV-02** | Review | Visual Silence & Pause Overlays | `Specified` | Milestone 6 | Color-coded badges |
| **REQ-REV-03** | Review | Transcript Text Correction | `Specified` | Milestone 6 | SQLite writeback |
| **REQ-REV-04** | Review | Speaker Label Management | `Specified` | Milestone 6 | Propagation check |
| **REQ-REV-05** | Review | Scene & Keyframe Inspector | `Specified` | Milestone 6 | Keyframe gallery |
| **REQ-EDT-01** | Timeline | Multitrack Timeline Model | `Specified` | Milestone 3 | Unlimited V/A/C tracks |
| **REQ-EDT-02** | Timeline | Non-Destructive Clip Operations | `Specified` | Milestone 3 | Add, cut, trim, move, split |
| **REQ-EDT-03** | Timeline | Transitions & Compositing | `Specified` | Milestone 3 | frei0r / cairoblend |
| **REQ-EDT-04** | Timeline | Effects & Filters | `Specified` | Milestone 3 | Audio & video filter stack |
| **REQ-EDT-05** | Timeline | Dynamic Jump Cuts & Punch-ins | `Specified` | Milestone 3 | 1.15x scale keyframing |
| **REQ-EDT-06** | Timeline | Synchronized Animated Captions | `Specified` | Milestone 3 | Word-level highlighting |
| **REQ-EDT-07** | Timeline | Native Kdenlive XML Serialization | `Specified` | Milestone 3 | Opens in Kdenlive 23.x/24.x |
| **REQ-EDT-08** | Timeline | Transactional Undo/Redo | `Specified` | Milestone 3 | Multi-level snapshot rollback |
| **REQ-MCP-01** | MCP | Stdio & SSE Transport Support | `Specified` | Milestone 4 | JSON-RPC stdio & SSE streams |
| **REQ-MCP-02** | MCP | Typed Project Tools | `Specified` | Milestone 4 | Pydantic validation |
| **REQ-MCP-03** | MCP | Typed Intelligence Tools | `Specified` | Milestone 4 | Intelligence queries |
| **REQ-MCP-04** | MCP | Typed Editing Tools | `Specified` | Milestone 4 | Clip operations via MCP |
| **REQ-MCP-05** | MCP | Typed Effects & Caption Tools | `Specified` | Milestone 4 | Effect parameters |
| **REQ-MCP-06** | MCP | Typed Rendering Tools | `Specified` | Milestone 4 | Job dispatch and status |
| **REQ-MCP-07** | MCP | Agent Collaboration Tools | `Specified` | Milestone 4 | Lock & event logging |
| **REQ-MCP-08** | MCP | Concurrency Locking & Validation | `Specified` | Milestone 4 | Interval overlap rejection |
| **REQ-AGT-01** | Orchestration | Specialized Agent Roles | `Specified` | Milestone 5 | 7 defined agent roles |
| **REQ-AGT-02** | Orchestration | Shared State & Event Ledger | `Specified` | Milestone 5 | Authoritative SQLite sync |
| **REQ-AGT-03** | Orchestration | Conflict Resolution | `Specified` | Milestone 5 | Interval locking |
| **REQ-AGT-04** | Orchestration | Agent Operational Provenance | `Specified` | Milestone 5 | Full action audit trail |
| **REQ-RPL-01** | Replay | Visual Event Reconstruction | `Specified` | Milestone 7 | Chronological ledger playback |
| **REQ-RPL-02** | Replay | Animated Color-Coded Cursors | `Specified` | Milestone 7 | 5 distinct agent cursors |
| **REQ-RPL-03** | Replay | Visual Timeline Manipulations | `Specified` | Milestone 7 | Bin drags, slices, stamps |
| **REQ-RPL-04** | Replay | Replay Scrubbing & Speed Control | `Specified` | Milestone 7 | 0.5x, 1x, 2x, 4x, restart |
| **REQ-RPL-05** | Replay | Deterministic Playback | `Specified` | Milestone 7 | Sandbox isolation check |
| **REQ-RND-01** | Render | Dual-Engine Renderer | `Specified` | Milestone 3 | MLT melt + FFmpeg filtergraph |
| **REQ-RND-02** | Render | Format & Aspect Ratio Presets | `Specified` | Milestone 3 | 16:9, 9:16, 1:1 MP4 |
| **REQ-RND-03** | Render | Progress & Graceful Cancellation | `Specified` | Milestone 3 | Subprocess cancellation |
| **REQ-RND-04** | Render | Output Verification | `Specified` | Milestone 3 | FFprobe header & duration test |

