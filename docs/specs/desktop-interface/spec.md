# Specification: Desktop Application Interface

## 1. Visual Design Philosophy & Aesthetics

AgentCut is designed as a **high-end, dark-themed, professional post-production environment** tailored for serious creators and video engineers. The interface draws inspiration from premium NLEs (DaVinci Resolve, Final Cut Pro) combined with modern collaborative workspaces (Figma, Linear).

- **Color Palette**: Deep obsidian grays (`#0D0F12`, `#16191E`, `#1F232B`) with high-contrast accent highlights (Electric Cyan `#00D9FF`, Studio Violet `#A55EEA`, Highlight Yellow `#FED330`).
- **Typography**: Clean, monospace-friendly sans-serif (`Inter`, `JetBrains Mono` for timecodes and logs).
- **Surface Elevation**: Subtle borders (`border-white/10`), frosted-glass backdrops (`backdrop-blur-md`), and silky 60 FPS transitions.

---

## 2. Workspace Layout & Screen Anatomy

```
+-------------------------------------------------------------------------------------------------------+
|  TOP BAR:  [Project: TikTok_Promo_V1]   (Saved)   ● MCP Connected (Port 8000)   [3 Agents Active] [EXPORT] |
+------------------------+----------------------------------------------------+-------------------------+
| LEFT PANEL:            | CENTER STAGE:                                      | RIGHT PANEL:            |
| [Project Media Bin]    | [Video Preview Monitor - 1080x1920 (9:16)]         | [Agent Activity & Logs] |
|                        |                                                    | ● Video Editor (Active) |
|  - raw_take_01.mp4     |                                                    |   "Cutting silence..."  |
|  - b_roll_coffee.mov   |  [Playhead Timecode: 00:00:14:12 / 00:00:45:00]    | ● Captioner (Active)    |
|  - music_upbeat.mp3    |  [|<] [<<] [ > / || ] [>>] [>|]  [Loop]  [Fit 100%] |   "Stamping text..."    |
|                        +----------------------------------------------------+-------------------------+
| [Intelligence Summary] | BOTTOM STAGE: MULTITRACK TIMELINE                  | [Inspector / Style]     |
| 98.4% Confidence STT   | Time Ruler: |--- 00:00 ---|--- 00:10 ---|--- 00:20 ---|--- 00:30 ---|---|     |
| 14 Pauses Detected     | Track C1 (Captions): [ "Welcome to today's..." ] [ "3 Rules..." ]            | - Color Grading         |
| 8 Scenes Identified    | Track V1 (Video):    [ Clip 1 (1.0x) ] [ Clip 2 (1.15x Punch) ]             | - Subtitle Typography   |
|                        | Track A1 (Audio):    [ ~~~~~ Dialog Waveform ~~~~~~~~~~~~~~~~~~ ]            | - Export Settings       |
|                        | Track A2 (Music):    [ ================= Background Music ================= ]|                         |
+------------------------+------------------------------------------------------------------------------+
```

---

## 3. Dedicated Views & Workflows

AgentCut provides 9 dedicated views accessible via the primary workspace navigation:

1. **Project Dashboard**: Project launcher, recent projects grid, resolution presets (16:9, 9:16, 1:1), and disk cache monitor.
2. **Media Import Screen**: Drag-and-drop ingestion zone with instant FFprobe metadata preview, codec inspection, and read-only validation badges.
3. **Video Analysis Screen**: Real-time progress visualizer tracking staged neural inference (VAD -> STT -> Diarization -> Scene Detection -> OCR) with VRAM allocation gauges.
4. **Analysis Review Interface**: Synchronized dual-pane view:
   - Interactive zoomable waveform with color-coded pause badges (Green = conversational, Orange = dramatic, Red = dead silence).
   - Click-to-seek transcript editor allowing creators to correct terminology and reassign speaker tags with instant SQLite sync.
5. **Editing Workspace**: The primary multitrack NLE view with video monitor, virtualized timeline canvas, snap-to-grid controls, and split/trim handles.
6. **Agent Activity Panel**: Live streaming telemetry showing agent task queues, interval locks, step-by-step reasoning logs, and conflict resolution alerts.
7. **Cinematic Replay Mode**: Full-stage animated studio showing multi-colored agent cursors collaborating in 60 FPS across the canvas with scrubbable speed controls and instant restart.
8. **Export Screen**: Production delivery console with format selectors (MP4, ProRes), aspect ratio transformers, bit rate controls, and real-time NVENC render monitors.
9. **Settings & Model Configuration**: Hardware manager configuring GPU device IDs, VRAM allocation ceilings, local model paths, and optional cloud LLM API tokens.

---

## 4. State Management & IPC Bridge

- **Electron Main Process**: Spawns FastAPI backend subprocess, controls window lifecycle, registers native menu shortcuts (e.g. `Space` for play/pause, `C` for razor tool, `Z` for undo), and handles file drag-and-drop.
- **Preload IPC Bridge**: Exposes a typed, context-isolated `window.agentCutAPI` bridge to the renderer, enforcing total separation from raw Node.js internals.
- **Frontend State (Zustand)**:
  - `useProjectStore`: Active project metadata, dimensions, tracks, and media bin items.
  - `usePlaybackStore`: Playhead timecode, playback status (playing/paused), volume, loop, and playback speed.
  - `useAgentStore`: Active registered agents, lock statuses, and real-time telemetry stream.
  - `useReplayStore`: Replay timeline offset, playback multiplier (0.5x, 1x, 2x, 4x), and active cursor keyframes.

