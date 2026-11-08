# Operations: Troubleshooting & Diagnostic Guide

## 1. Common Issues & Resolutions

### Issue 1: CUDA Out of Memory (OOM) during Intelligence Processing
- **Symptoms**: Error message `torch.cuda.OutOfMemoryError: CUDA out of memory. Tried to allocate...`
- **Cause**: Background GPU applications (games, 3D renderers, or un-purged Whisper instances) are consuming VRAM, exceeding the 6GB capacity.
- **Diagnostic**: Run `nvidia-smi` in PowerShell to inspect active GPU memory consumers.
- **Resolution**:
  1. Close non-essential GPU background applications.
  2. In AgentCut Settings, verify that `VRAM Limit` is set to `4000 MB` or lower.
  3. Force sequential model loading; ensure `VRAMLifecycleManager` executes `torch.cuda.empty_cache()` between pipeline stages.
  4. Fall back to `CPU` inference mode for transcription (`CTranslate2 INT8` on the 16-thread Ryzen 7 CPU still runs in ~30s for a 5-minute audio track).

---

### Issue 2: `melt` Command Not Recognized or Render Fails
- **Symptoms**: Backend logs show `FileNotFoundError: [WinError 2] The system cannot find the file specified: 'melt'`.
- **Cause**: MLT command line tools are not present in Windows PATH.
- **Resolution**:
  1. AgentCut automatically fails over to the **Native FFmpeg Fallback Engine**; check the render log to verify FFmpeg execution.
  2. If native MLT rendering is desired, install Kdenlive from `https://kdenlive.org/` or via winget:
     ```powershell
     winget install KDE.Kdenlive
     ```
  3. Add `C:\Program Files\kdenlive\bin` to your System PATH or enter the path in AgentCut Settings under **MLT melt executable path**.

---

### Issue 3: MCP Agent Receives `ResourceLockedException`
- **Symptoms**: External agent reports failure when calling `split_clip` or `trim_clip`: `Interval [12.0, 24.5] on track V1 is locked by agent video_editor_1`.
- **Cause**: Another agent is currently editing that timeline section, or an earlier crashed transaction did not release its lock.
- **Resolution**:
  1. Locks have a strict 10-second automatic lease expiration. Wait 10 seconds and retry.
  2. Alternatively, invoke the MCP tool `force_release_locks(project_id="...")` to clear stale locks.

---

### Issue 4: Displaced Audio/Video Synchronization after Cuts
- **Symptoms**: In the exported video, audio drifts by a fraction of a second after multiple jump cuts.
- **Cause**: Source video has a Variable Frame Rate (VFR) or audio sample rate mismatch (44.1kHz vs 48kHz).
- **Resolution**:
  1. During ingestion, AgentCut checks for VFR streams.
  2. If VFR is detected, enable **Transcode to Constant Frame Rate (CFR) Proxy** in Media Ingestion settings.
  3. Ensure all extracted audio tracks are standardized to 48kHz 16-bit PCM before timeline assembly.

