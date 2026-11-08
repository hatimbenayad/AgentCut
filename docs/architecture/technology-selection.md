# AgentCut: Technology Selection & Benchmark Evaluation

## 1. Technology Evaluation Matrix

| Category | Candidate Technologies | Selected Choice | Rationale & Trade-offs |
| :--- | :--- | :--- | :--- |
| **Desktop Shell** | Electron vs Tauri vs PyQt/PySide | **Electron (TypeScript)** | Mature multimedia playback ecosystem, native HTML5 video hardware decoding, rich DOM/Canvas layering for Framer Motion cursor animations, seamless Node.js IPC with Python subprocesses. Tauri has lighter binary size but webview video codec quirks on Windows. |
| **UI Framework** | React 18 + Tailwind vs Vue 3 vs Svelte | **React 18 + Tailwind + Framer Motion** | Vast ecosystem of high-performance timeline virtualizers, declarative state management (Zustand), and fluid 60fps spring animations essential for the multi-cursor replay. |
| **Backend Service** | FastAPI (Python) vs Express (Node) vs Go | **FastAPI (Python 3.13)** | Python is mandatory for direct integration with AI models (CTranslate2, ONNX, PyTorch, OpenCV). FastAPI offers async I/O, Pydantic type validation, and high-performance WebSockets. |
| **Video Editing Format** | Kdenlive (MLT XML) vs OTIO vs Custom JSON | **Kdenlive / MLT XML (`.kdenlive`)** | Native interoperability with Kdenlive desktop NLE, proven multi-track video/audio compositor, open declarative XML format, rich filter ecosystem. |
| **Rendering Engine** | MLT `melt` vs Native FFmpeg | **Dual Engine: MLT `melt` + FFmpeg** | `melt` provides native `.kdenlive` project rendering; FFmpeg filtergraph engine provides zero-setup fallback rendering ensuring out-of-the-box reliability on any Windows PC. |
| **Speech-to-Text** | `faster-whisper` vs OpenAI Whisper vs WhisperX | **`faster-whisper` (CTranslate2)** | 4x faster execution, 50% lower VRAM usage than vanilla PyTorch Whisper; supports word-level timestamps, handles English and Spanish with high accuracy. |
| **Voice Activity Detection** | Silero VAD vs WebRTC VAD | **Silero VAD (ONNX)** | Superior precision in distinguishing speech, conversational breath pauses, and acoustic dead air compared to simple energy thresholds. Ultra-light (<50MB). |
| **Scene Detection** | PySceneDetect vs Custom OpenCV diff | **PySceneDetect (ContentDetector)** | Industry-standard scene boundary detection with adaptive thresholding; runs multithreaded on CPU with zero VRAM overhead. |
| **On-Screen OCR** | RapidOCR (ONNX) vs PaddleOCR vs Tesseract | **RapidOCR (ONNX Runtime)** | Runs PP-OCRv4 models directly on ONNX Runtime with official Python 3.13 Windows wheels, avoiding heavy C++ build issues and PaddlePaddle CUDA conflicts. |
| **Visual Description** | Qwen2.5-VL-3B-Instruct (Quantized) | **Qwen2.5-VL-3B (AWQ/GGUF) + Cloud Adapter** | Fits within 2.5GB VRAM when loaded in 4-bit; provides rich semantic context ("host gesturing to whiteboard", "b-roll product shot"). Includes cloud API adapter fallback. |
| **Agent Interface** | Model Context Protocol (MCP) vs REST only | **FastMCP (stdio & SSE)** | Industry standard protocol for AI agent tool integration; supports Claude Desktop, Codex, Antigravity, and autonomous agent frameworks seamlessly. |
| **State Persistence** | SQLite (WAL mode) vs PostgreSQL vs JSON | **SQLite (WAL mode)** | Zero-configuration single-file database per project; ACID compliance, instant transactional snapshots, and high-throughput logging of replay events. |

---

## 2. Licensing and Open-Source Compliance

| Dependency / Model | License | Distribution & Commercial Use Compliance |
| :--- | :--- | :--- |
| **MLT Framework** | LGPL v2.1+ / GPL v2 | Compliant. Executed as an external CLI process (`melt.exe`), preventing viral license contamination of AgentCut source code. |
| **Kdenlive Project Schema** | GPL v3 | Compliant. Project files (`.kdenlive`) are standard XML documents; manipulating and writing open XML formats is non-infringing. |
| **FFmpeg** | LGPL v2.1+ / GPL v2+ | Compliant. Distributed and executed via standard CLI subprocess calls. |
| **faster-whisper** | MIT License | Fully permissive for open-source and commercial use. OpenAI Whisper weights are MIT licensed. |
| **Silero VAD** | MIT License | Fully permissive. |
| **PySceneDetect** | BSD 3-Clause | Fully permissive. |
| **RapidOCR (PaddleOCR weights)**| Apache 2.0 | Fully permissive. |
| **Qwen2.5-VL-3B-Instruct** | Apache 2.0 | Fully permissive commercial and research use. |
| **Python MCP SDK** | MIT License | Fully permissive. |
| **Electron & React** | MIT License | Fully permissive. |

---

## 3. Hardware Benchmark & Target Performance Targets

Tested against target configuration:
- **Processor**: AMD Ryzen 7 7435HS (8 Cores, 16 Threads @ 3.1 GHz - 4.5 GHz)
- **Memory**: 24 GB DDR5 RAM
- **GPU**: NVIDIA GeForce RTX 4050 Laptop GPU (6 GB GDDR6 VRAM, TGP 75W, CUDA 13.4, Driver 617.42)
- **Storage**: PCIe Gen4 NVMe SSD

### Target Throughput & Latency Budgets
1. **Audio Extraction**: < 3 seconds for a 10-minute 1080p video.
2. **Silero VAD Processing**: < 2 seconds for a 10-minute audio track (CPU).
3. **`faster-whisper` (base/small model)**: ~30-45 seconds for a 10-minute audio track (CUDA FP16).
4. **PySceneDetect Cut Detection**: ~15-20 seconds for 10 minutes of 1080p footage (CPU multi-threading).
5. **RapidOCR on Sampled Keyframes**: ~100ms per keyframe (ONNX Runtime).
6. **Timeline Mutation via MCP**: < 50ms per tool invocation.
7. **Replay Rendering**: Solid 60 FPS with Framer Motion GPU hardware composition.

