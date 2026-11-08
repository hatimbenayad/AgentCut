# AgentCut: Known Technical Limitations & Mitigation Strategies

This document catalogs identified technical limitations, hardware boundaries, and architectural mitigations.

---

## 1. Hardware & VRAM Constraints (6GB Laptop GPU)

### Limitation
The target development machine utilizes an **NVIDIA GeForce RTX 4050 Laptop GPU with 6GB VRAM** (~4.8GB available after Windows OS allocation). Loading multiple large neural models simultaneously (e.g., Whisper + Pyannote Diarization + Qwen-VL) immediately triggers CUDA Out-Of-Memory (OOM).

### Mitigation
- **Strict Sequential Staging**: The `VRAMLifecycleManager` enforces single-model residency. Each neural model is loaded, executed across batch segments, unloaded, and followed by explicit `torch.cuda.empty_cache()` and `gc.collect()`.
- **CPU Offloading**: Scene change detection (`PySceneDetect`), audio waveform computation, and FFmpeg proxy rendering are assigned exclusively to CPU worker pools (8 cores / 16 threads AMD Ryzen 7 7435HS).
- **Quantization**: Whisper models use CTranslate2 INT8/FP16; VLM models use 4-bit AWQ or fallback to pluggable cloud vision inference if local VRAM is constrained.

---

## 2. MLT Framework (`melt`) Windows Environment Availability

### Limitation
On standard Windows machines, MLT's command line binary (`melt.exe`) is not present in the default system PATH unless the user has installed Kdenlive or Shotcut and manually configured environment variables. If an editing application solely depends on `melt` for rendering, clean machine installations will fail to produce video deliverables.

### Mitigation
- **Dual-Engine Rendering**: AgentCut generates authentic, production-grade `.kdenlive` XML project files, but its rendering controller features a **Native FFmpeg Fallback Engine**. The timeline model can compile directly into a dynamic FFmpeg `-filter_complex` pipeline, enabling instantaneous rendering on any machine equipped with standard FFmpeg (already verified on the target machine at `8.0.1`).
- **Path Auto-Discovery**: AgentCut scans standard Kdenlive installation directories (`C:\Program Files\kdenlive\bin\melt.exe`) and allows the user to specify a custom `melt` path in settings.

---

## 3. Optical Character Recognition (OCR) Duplication

### Limitation
Standard frame-by-frame OCR creates hundreds of redundant events when static titles, lower-thirds, or slide text remain on screen for seconds or minutes.

### Mitigation
- **Temporal IoU & Levenshtein Tracking**: AgentCut samples keyframes adaptively and executes a temporal tracking algorithm. Detections across sequential frames sharing $>60\%$ bounding box IoU and $>80\%$ string similarity are merged into a single event with an estimated start and end duration `[t_start, t_end]`.

---

## 4. Disfluency vs. Deliberate Speech Pacing

### Limitation
Aggressive automatic cutting of silences destroys dramatic tension, thoughtful pacing, and natural conversational flow. A long pause before an important revelation is artistically desirable, not a defect.

### Mitigation
- **Acoustic & Semantic Pause Classification**: AgentCut classifies non-speech intervals into micro-pauses (<0.4s), conversational breath pauses (0.4s - 0.8s), dramatic pauses (0.8s - 1.5s), and dead air (>1.5s). Pauses preceding significant semantic shifts or accompanied by pitch descents are tagged `dramatic_pause` with `recommended_action: preserve`.
- **Human Review Gate**: Creators can inspect and toggle pause classifications in the Analysis Review panel before agents execute cuts.
- **Source Immutability**: All cuts are virtual timeline clips; any cut pause can be instantly restored by expanding clip in/out handles.

