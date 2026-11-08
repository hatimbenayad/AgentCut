# AgentCut: User Stories & Acceptance Criteria

## User Story 1: Intelligent Footage Ingestion & Analysis
**As a** video creator,  
**I want to** import a 20-minute unedited talking-head recording into AgentCut and have it automatically analyzed,  
**So that** I get an accurate transcript, speech-silence map, detected speaker boundaries, and visual scene cuts without manual tagging.

### Acceptance Criteria:
- [ ] User drags and drops `interview.mp4` into the Media Bin.
- [ ] Video metadata (duration, fps, resolution) appears within 2 seconds.
- [ ] Progress indicators display the staged analysis: Audio Extraction -> Silero VAD -> faster-whisper Transcription -> Scene Detection -> Keyframe OCR.
- [ ] Analysis completes without exceeding 4.0 GB VRAM.
- [ ] Unified analysis JSON is generated and persisted in the project SQLite database.

---

## User Story 2: Human Analysis Review & Rapid Correction
**As a** technical editor,  
**I want to** inspect the transcript, silence segments, and detected text before the AI starts cutting,  
**So that** I can fix misheard proper nouns or adjust pause classifications.

### Acceptance Criteria:
- [ ] User can click any word in the transcript; the preview video instantly seeks to that word's start time.
- [ ] Pauses are visually color-coded on the waveform (Green = natural pause, Orange = dramatic emphasis, Red = dead silence).
- [ ] Editing a typo in the transcript updates the word record in the SQLite store immediately.
- [ ] Renaming `speaker_0` to "Alex" propagates across all associated speech segments.

---

## User Story 3: Autonomous AI Editing via Natural Language Prompt
**As a** solo social media marketer,  
**I want to** give a prompt like *"Create a punchy 45s TikTok highlighting the 3 main productivity hacks with animated yellow captions and vertical 9:16 framing"*,  
**So that** external AI agents formulate a complete edit plan and construct the timeline.

### Acceptance Criteria:
- [ ] Director Agent decomposes prompt into a structured Edit Plan.
- [ ] Footage Analyst identifies relevant clips by querying the intelligence database via MCP.
- [ ] Video Editor cuts dead air, creates dynamic jump cuts with 1.15x punch-ins, and places them onto Track V1.
- [ ] Caption Designer places animated, word-highlighted captions onto the Caption Track.
- [ ] Timeline updates smoothly in real time or upon batch execution.
- [ ] All edits are non-destructive and can be undone via Ctrl+Z.

---

## User Story 4: Cinematic Multi-Agent Collaborative Replay
**As a** producer or client,  
**I want to** watch an animated, cinematic replay of how the different AI agents assembled the video,  
**So that** I can understand the creative decisions and verify which agent executed each cut.

### Acceptance Criteria:
- [ ] User clicks the **Cinematic Replay** tab.
- [ ] Cursors representing the active agents (e.g., Cyan for Video Editor, Yellow for Caption Designer) appear on screen.
- [ ] Timeline clips visibly slide into place, razor splits animate with particle/haptic feedback, and captions pop in sync with the recorded event timestamps.
- [ ] User can adjust playback speed (0.5x, 1x, 2x, 4x), scrub the replay timeline, pause, or click **Restart Replay**.
- [ ] Replay does not modify or corrupt the actual project timeline.

---

## User Story 5: Production Rendering & Kdenlive Compatibility
**As a** professional video editor,  
**I want to** render a final MP4 export directly from AgentCut and open the identical project in Kdenlive desktop,  
**So that** I have full freedom to perform manual fine-tuning in my favorite NLE.

### Acceptance Criteria:
- [ ] Project can be rendered headlessly to 1080p 60fps MP4 (16:9 or 9:16) with progress bar and ETA.
- [ ] Render output is verified for audio sync and non-zero byte size.
- [ ] User can click "Open in Kdenlive" or open `project.kdenlive`; all tracks, cut clips, transitions, and audio levels load identically in Kdenlive 23.x/24.x.

