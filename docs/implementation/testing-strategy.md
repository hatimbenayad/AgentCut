# AgentCut: Comprehensive Testing & Quality Assurance Strategy

## 1. Testing Pyramid

To ensure that AgentCut functions reliably and adheres strictly to the Definition of Done, testing is structured across four distinct verification tiers:

```mermaid
pyramid
    title Testing Pyramid
    "Tier 4: End-to-End System & DoD Workflows" : 10
    "Tier 3: Subsystem Integration & MCP Contract Tests" : 30
    "Tier 2: Timeline Math & Intelligence Unit Tests" : 60
    "Tier 1: Data Model Schemas & Invariant Validations" : 100
```

---

## 2. Test Suites by Subsystem

### 2.1 Video Intelligence Engine Tests (`tests/test_intelligence/`)
- **VAD Accuracy Test**: Run Silero VAD on synthesized audio containing known intervals of speech and calibrated silence (0.2s, 0.6s, 1.2s, 2.5s). Verify categorization into micro, conversational, dramatic, and dead silence.
- **Timestamp Alignment Test**: Transcribe a reference speech recording with ground-truth word timestamps. Ensure word `start` and `end` times are within $\pm 50 \text{ ms}$ of ground truth.
- **Disfluency Detector Test**: Evaluate English and Spanish test samples containing deliberate stutters ("um", "like", "este", "bueno") and repeated phrases. Verify extraction of correct word IDs.
- **Scene Change Detection Test**: Process a multi-cut test video. Verify that `PySceneDetect` detects cut frames with zero false negatives.
- **Temporal OCR Deduplication Test**: Feed 10 consecutive frames containing identical static text. Verify that the output contains exactly 1 consolidated event with start/end duration matching the frame sequence.
- **VRAM Leak Test**: Run the full intelligence pipeline 5 times consecutively on a 1-minute video. Verify that peak GPU VRAM usage returns to baseline after each iteration with zero CUDA memory leaks.

### 2.2 Timeline & MLT XML Engine Tests (`tests/test_timeline/`)
- **Virtual Clip In/Out Invariant Test**: Assert that for any clip, $S_{out} - S_{in} = T_{out} - T_{in}$ (assuming speed = 1.0).
- **Split Clip Test**: Split a clip at arbitrary timestamps. Assert that the sum of the two split durations equals the original duration and that no frames are skipped or duplicated.
- **Kdenlive XML Round-Trip Test**: Construct a multi-track project in memory with transitions, color filters, and title captions. Serialize to `.kdenlive` XML, parse back into a new timeline object, and assert complete structural equality.
- **Undo / Checkpoint Test**: Execute 10 sequential edits, trigger undo 5 times, and verify that the timeline state matches the checkpoint snapshot at edit #5.

### 2.3 MCP Server Contract Tests (`tests/test_mcp/`)
- **Schema Validation Test**: Test all MCP tool endpoints (`create_project`, `add_video_clip`, `split_clip`, `render_video`) against malformed arguments, out-of-range timestamps, and invalid track indices. Ensure structured Pydantic error responses are returned.
- **Concurrency & Lock Test**: Simulate two concurrent agents attempting to edit identical track intervals simultaneously. Verify that agent 1 acquires the lock and agent 2 receives a `ResourceLockedException`.
- **Event Ledger Logging Test**: Execute editing tools via MCP and assert that matching rows are written to the SQLite `editing_events` table with correct `agent_id`, `agent_color`, and timestamp coordinates.

### 2.4 Rendering & Export Verification Tests (`tests/test_rendering/`)
- **Dual-Engine Output Test**: Render a test project with both MLT `melt` and the native FFmpeg engine. Verify that both produce playable MP4 files with identical track compositions.
- **Integrity Gate Test**: Verify that corrupt files, 0-byte outputs, or duration mismatches (> 0.2s) cause the render job to fail with a clear, descriptive error code.
- **Aspect Ratio Transform Test**: Render a 16:9 source to 9:16 vertical. Verify that the output video stream has dimensions $1080 \times 1920$ with correct center cropping.

### 2.5 Cinematic Replay Tests (`tests/test_replay/`)
- **Deterministic Trajectory Test**: Given an event ledger containing 10 events, run the visual path generator twice. Verify that generated cursor coordinates and duration curves are mathematically identical.
- **Sandboxing Invariant Test**: Run a full 60-second replay session. Verify that no disk writes occur to source media or `.kdenlive` project files during replay.

---

## 3. Automated Test Execution Commands

```bash
# Run all unit and schema tests
pytest tests/unit -v

# Run Video Intelligence pipeline tests (CPU & GPU)
pytest tests/test_intelligence -v -m "not heavy_gpu"

# Run Timeline and Kdenlive XML tests
pytest tests/test_timeline -v

# Run MCP server contract tests
pytest tests/test_mcp -v

# Run full end-to-end integration suite
pytest tests/integration -v
```

