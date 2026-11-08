# AgentCut: Architecture Decision Records (ADRs)

## ADR-001: Selection of MLT Multimedia Framework and Kdenlive XML Project Format

### Context
AgentCut requires a non-linear video editing (NLE) backend that supports multi-track video, audio, transitions, effects, titles, color adjustments, and headless rendering. We evaluated several alternatives:
1. **Custom FFmpeg script generation only**: Flexible, but produces no editable native project file for human editors to fine-tune in an established desktop NLE.
2. **OpenTimelineIO (OTIO)**: Standardized industry interchange schema, but OTIO has no built-in rendering engine or transition/filter DSP ecosystem.
3. **Blender VSE (Video Sequence Editor)**: Scriptable via Python, but bulky, slow to render, and not designed as a headless background NLE.
4. **MLT Multimedia Framework & Kdenlive XML (`.kdenlive`)**: Mature open-source C/C++ engine, battle-tested across decades, powers both Kdenlive and Shotcut, has a declarative XML project schema (`<tractor>`, `<playlist>`, `<producer>`), supports complex transitions (`frei0r`, `cairoblend`), and renders headlessly via the `melt` CLI.

### Decision
We choose **MLT Multimedia Framework and the Kdenlive XML project format (`.kdenlive`)** as AgentCut's native project file format.

### Consequences
- **Positive**: Complete interoperability with the desktop Kdenlive editor. A user can open any AgentCut-generated `.kdenlive` project directly in Kdenlive 23.x/24.x.
- **Positive**: Clean declarative XML schema that AI agents can inspect, construct, and validate deterministically.
- **Positive**: Rich built-in filters (frei0r, LADSPA audio filters, avfilter bindings, affine transforms).
- **Negative / Mitigation**: MLT's `melt` CLI tool may not always be in the user's system PATH on clean Windows machines. We mitigate this via **ADR-002 (Dual-Engine Rendering Architecture)**.

---

## ADR-002: Dual-Engine Rendering Architecture (MLT `melt` + FFmpeg Filtergraph Fallback)

### Context
While MLT's `melt` is the ideal renderer for `.kdenlive` files, installing MLT on Windows can sometimes require installing the full Kdenlive package or configuring complex environment paths. FFmpeg, conversely, is already universally available on Windows development systems (and verified at `8.0.1-full_build` on our target machine).

### Decision
AgentCut implements a **Dual-Engine Rendering Architecture**:
1. **Primary Engine (MLT `melt`)**: If `melt.exe` is detected on the system or configured in settings, AgentCut passes the `.kdenlive` XML directly to `melt -progress <project.kdenlive> -consumer avformat:<output.mp4> ...`.
2. **Built-in Fallback Engine (Native FFmpeg Filtergraph Generator)**: AgentCut includes an internal timeline compiler that translates the abstract timeline data model (tracks, cuts, transitions, volume, speed, animated subtitles) directly into a complex FFmpeg filtergraph (`-filter_complex`), enabling 100% out-of-the-box headless rendering without requiring MLT to be installed first.

### Consequences
- **Positive**: Zero initial friction. AgentCut renders finished videos immediately using existing FFmpeg while still generating authentic, fully valid `.kdenlive` files for desktop Kdenlive users.
- **Positive**: High resilience: if `melt` encounters a plugin missing error on an exotic transition, the FFmpeg engine provides a reliable fallback.

---

## ADR-003: Sequential Staged VRAM Lifecycle for 6GB Laptop GPU Constraint

### Context
The target hardware features an **NVIDIA GeForce RTX 4050 Laptop GPU with 6GB VRAM** (~4.8 GB free VRAM after Windows DWM allocation). Running `faster-whisper` (1.5 GB), `pyannote.audio` (1.6 GB), and `Qwen2.5-VL-3B` (2.4 GB) concurrently would require > 5.5 GB VRAM, triggering fatal CUDA Out-Of-Memory (OOM) crashes.

### Decision
We mandate a **Strict Sequential Model Lifecycle Architecture** managed by a central `VRAMLifecycleManager`:
1. Neural models are never kept permanently resident in GPU memory.
2. Inference is executed in sequential stages:
   - **Stage 1**: Silero VAD (ONNX/CPU, 50MB) + `faster-whisper` (CUDA, 1.5GB) -> run transcription -> explicit PyTorch CUDA cache flush (`torch.cuda.empty_cache()`, `gc.collect()`).
   - **Stage 2**: Speaker Diarization (Pyannote) -> run diarization -> unload from VRAM.
   - **Stage 3**: Visual Scene Detection (`PySceneDetect`) and Keyframe extraction run purely on CPU/OpenCV multi-threading (0 MB VRAM).
   - **Stage 4**: On-screen OCR (`RapidOCR`) runs on ONNX Runtime (CPU or lightweight GPU ~400 MB).
   - **Stage 5**: Visual description (`Qwen2.5-VL-3B` quantized) is loaded only on selected keyframes, then purged.

### Consequences
- **Positive**: Peak VRAM remains capped below **3.2 GB**, comfortably within the 4.8 GB free VRAM limit.
- **Positive**: Rock-solid stability on laptop GPUs without throttling or OOM crashes.
- **Negative / Mitigation**: Model load/unload overhead adds ~1.5 - 2.5 seconds per pipeline stage. For videos lasting minutes to hours, this 5-second aggregate overhead is negligible.

---

## ADR-004: RapidOCR (ONNX Runtime) with IoU Temporal Box Tracking

### Context
The video intelligence engine must detect on-screen text (lower thirds, chapter titles, slides, URLs). Standard `PaddleOCR` on Windows frequently encounters heavy PaddlePaddle C++ DLL dependency conflicts and Python 3.13 compatibility barriers. Furthermore, running naive OCR on every frame creates thousands of duplicate text records.

### Decision
1. We adopt **`RapidOCR` (ONNX Runtime)** as the primary OCR engine, which runs the official PaddlePaddle PP-OCRv4 models using standard `onnxruntime` wheels, verified compatible with Windows and Python 3.13.
2. We implement a **Temporal Box Tracker**:
   - Compares bounding boxes across adjacent sampled keyframes using spatial **Intersection-over-Union (IoU > 0.6)** and textual **Levenshtein Distance (> 80% similarity)**.
   - Merges identical text appearing across multiple seconds into a single consolidated event `[t_start, t_end]` with average bounding box coordinates.

### Consequences
- **Positive**: High speed, zero C++ compiling friction, low memory footprint (~400 MB).
- **Positive**: Clean, deduplicated intelligence database with exact appearance/disappearance intervals.

---

## ADR-005: Model Context Protocol (MCP) as Universal AI Control Layer

### Context
AgentCut must be controllable by external AI agents without being locked into any single proprietary LLM provider.

### Decision
We implement a standalone **Model Context Protocol (MCP) Server** following the official specification. It exposes structured tools categorized into:
- Project & Asset Management (`create_project`, `import_media`, etc.)
- Intelligence Inspection (`get_transcript`, `get_silence_segments`, etc.)
- Timeline Editing (`add_video_clip`, `split_clip`, `trim_clip`, `punch_in`, etc.)
- Styling & Captions (`generate_captions`, `style_captions`, `adjust_color`, etc.)
- Rendering (`render_video`, `get_render_status`)
- Agent Coordination (`register_agent`, `publish_editing_event`, `create_checkpoint`)

### Consequences
- **Positive**: Instant interoperability with Claude Desktop, Cursor, Codex, Antigravity, and custom agent loops over standard stdio or SSE.
- **Positive**: Strongly typed Pydantic request/response schemas with automated input validation.

---

## ADR-006: Deterministic Event-Ledger-Driven Multi-Cursor Replay Studio

### Context
AgentCut requires a signature visual experience: an animated multi-cursor replay showing how AI agents collaborated to produce the edit. If the animation were merely decorative or randomized, it would violate engineering integrity and mislead creators.

### Decision
We build the **Cinematic Replay Engine** directly on top of the **authoritative SQLite Event Ledger**:
1. Every real edit executed by an agent writes an immutable event record containing `event_id`, `agent_id`, `agent_name`, `agent_color`, `action_type`, `target_track`, `timeline_position`, `duration`, and `visual_metadata` (e.g. source clip rect, target track rect).
2. The replay engine acts as a **visual interpreter**: it processes this recorded ledger deterministically in chronological order.
3. The Replay UI animates actual cursor positions, drag-and-drop motions, razor splits, and caption placements using Framer Motion at 60 FPS.
4. Scrubbing, playback speed (0.5x, 1x, 2x, 4x), and an instant **Restart Animation** button allow the user to inspect any phase of the collaborative session without mutating project data.

### Consequences
- **Positive**: 100% deterministic, truthful representation of actual multi-agent operations.
- **Positive**: Replayable at any time, even weeks after the project was rendered.
- **Positive**: Complete visual isolation: replay runs in a separate visual sandbox that cannot corrupt the `.kdenlive` project.

---

## ADR-007: SQLite with WAL Mode as Authoritative State and Event Ledger Store

### Context
AgentCut requires persistent storage for video intelligence records, timeline snapshots, agent activity logs, and project metadata. Storing everything in loose JSON files leads to race conditions, partial writes, and slow queries.

### Decision
We use an embedded **SQLite database with Write-Ahead Logging (WAL mode)** per project (`project.db`).

### Consequences
- **Positive**: Single-file storage alongside media assets; zero external database service configuration.
- **Positive**: WAL mode allows concurrent non-blocking reads (by the UI and MCP agents) while writes are committed in microseconds.
- **Positive**: ACID transactions protect project integrity against sudden power loss or process crashes.

---

## ADR-008: Source Media Immutability and Virtual In/Out Clipping

### Context
AI agents must never overwrite, truncate, or corrupt original user footage.

### Decision
1. Ingested source files are opened exclusively in read-only mode (`O_RDONLY`).
2. Timeline edits are purely **virtual**: clips on tracks only store metadata references (`asset_id`, `source_in`, `source_out`, `timeline_in`, `timeline_out`).
3. Trimming, splitting, or deleting a clip simply adjusts or removes virtual metadata records; the underlying source media on disk remains bit-for-bit identical.

### Consequences
- **Positive**: Total data safety. Creators can never lose footage due to an aggressive AI trimming decision.
- **Positive**: Instant undo/redo capability with zero disk I/O duplication.



---

## ADR-009: Adoption of Canonical Typed Timeline Model over Native Kdenlive File as Source of Truth

### Context
Suggestion S2 advised evaluating whether to use a typed, versioned canonical timeline model stored in SQLite/JSON as the single source of truth, compiling to MLT XML for rendering and optional Kdenlive export, rather than directly parsing and patching `.kdenlive` XML.

### Empirical Experiment (Milestone 1)
In `experiments/timeline_mlt/test_timeline_compile.py`, we implemented a typed Canonical Timeline Model (`TrackModel`, `ClipModel`, `TextOverlayModel`) and tested:
1. Compilation to `.kdenlive` MLT XML.
2. Direct compilation to an FFmpeg `-filter_complex` filtergraph.
3. Programmatic rendering and duration verification.

**Empirical Results:**
- The canonical model compiled to a valid `.kdenlive` XML (1,104 bytes) with zero schema drift.
- The canonical model compiled directly to an FFmpeg filtergraph and rendered an exact 6.00-second 720p 30fps MP4 with a 1.15x punch-in jump cut and yellow subtitle overlay in **0.58 seconds**.
- An inspection of Windows systems revealed that `melt.exe` is not installed by default on clean Windows systems. Direct XML dependency would cause immediate failure on machines without Kdenlive pre-installed.
- Programmatically mutating raw XML (frame calculations, element insertion, blank padding, namespace preservation) required >150 lines of brittle string/element manipulation per cut, compared to 1 atomic method call on the canonical model.

### Decision
**ADOPTED.** The canonical typed data model stored in SQLite is the sole authoritative source of truth for the project. Kdenlive MLT XML is an exported compilation target, ensuring:
1. Transactional undo/redo and checkpoint rollbacks operate with zero XML corruption risk.
2. Direct dual-engine rendering (FFmpeg built-in + MLT `melt` when available).
3. Conflict detection and fine-grained interval locking operate on typed records.
4. Seamless event generation for the Cinematic Replay engine.

---

## ADR-010: Adoption of Coarser, Ergonomic MCP Tool Surface (~20 High-Leverage Tools)

### Context
Suggestion S5 advised avoiding an overly fine-grained tool surface (e.g., 60 individual micro-tools) which exhausts LLM token limits and causes hallucinated tool sequencing.

### Decision
**ADOPTED.** The MCP server groups capabilities into **20 high-leverage, strongly typed tools with rich parameters**:
- `project_manage`: Combined lifecycle (create, open, save, get_info, get_timeline).
- `media_ingest`: Ingestion, metadata extraction, waveform generation.
- `intelligence_query`: Unified query interface (`get_transcript`, `get_silences`, `get_ocr`, `search_content`).
- `edit_timeline`: Atomic batch editing accepting a typed array of operations (`insert`, `split`, `trim`, `move`, `delete`, `punch_in`).
- `apply_captions`: Synchronized subtitle generation and styling.
- `apply_effects`: Transitions, color grading, and audio normalization.
- `render_dispatch`: Export job initiation with preset, aspect ratio, and cancellation.
- `collab_control`: Agent registration, interval locks, and checkpoint undo.

All operations execute inside atomic SQLite transactions and emit structured provenance records to the event ledger.

---

## ADR-011: Unified Core Service as Single Source of Truth (Preventing Split-Brain State)

### Context
Suggestion S8 warned against allowing the MCP server and desktop UI to run as separate processes that independently mutate project files.

### Decision
**ADOPTED.** A single local backend service (`agentcut.backend`) hosts the SQLite database and timeline state. The desktop Electron UI communicates via REST/WebSockets, while external agents communicate via the FastMCP server connected to this exact same backend service. All mutations pass through the same concurrency and lock manager.

---

## ADR-012: Adoption of Vertical Slice Delivery (Revised Roadmap)

### Context
Suggestion S4 recommended delivering a working end-to-end vertical slice early to prove the full workflow before expanding into secondary features.

### Decision
**ADOPTED.** Milestone 2 is re-scoped to deliver the **End-to-End Vertical Slice**:
- Audio extraction + Silero VAD + faster-whisper STT + PySceneDetect cuts.
- Unified JSON intelligence export.
- Canonical timeline model creation, clip trimming, and punch-in jump cut.
- Headless rendering to verified MP4.
- Event ledger recording real operations.
- Cinematic Replay prototype demonstrating multi-cursor playback.

Advanced features (Pyannote speaker diarization, Qwen2.5-VL visual semantics, multi-aspect 9:16 export, full NLE UI panels) follow in subsequent milestones.

---

## ADR-013: Model Pinning & Runtime Environment for Windows

### Context
Suggestion S6 advised empirical validation of neural models on the target hardware (Windows 11, AMD Ryzen 7 7435HS, NVIDIA RTX 4050 Laptop GPU).

### Empirical Results:
1. `rapidocr-onnxruntime`: Ran in **606ms** on ONNX Runtime; detected text with 0.86 confidence. Eliminates heavy PaddlePaddle C++ conflicts.
2. `scenedetect`: Executed scene detection across 5s footage in **0.60s** on CPU.
3. `faster-whisper`: Encountered PyAV v19 incompatibility (`TypeError: metadata_errors`). Resolved by pinning **`av<14`** (`av==13.1.0`).
4. **CTranslate2 Execution:** On Windows without separate CUDA 12 toolkit DLLs (`cublas64_12.dll`), `faster-whisper` running on CPU (`int8`) transcribed 5s of audio in **0.48 seconds** on the 16-thread Ryzen 7 CPU (>10x faster than real-time playback) with instant model unloading and zero VRAM footprint!

### Decision
**ADOPTED.** We pin `av<14`, use `rapidocr-onnxruntime`, and implement dynamic engine dispatch: CUDA FP16 when CUDA 12 DLLs are present, with automatic zero-error fallback to CPU INT8.
