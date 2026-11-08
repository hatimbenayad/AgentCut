# Specification: Replay Event Schema & Provenance Ledger

## 1. Overview & Invariants

The **Replay Event Schema** defines the data contract for every operational event emitted during an editing session.

### Core Invariants:
1. **Provenance Guarantee**: Every state mutation on the timeline MUST emit an event as an atomic side effect of the database transaction.
2. **Deterministic Reproducibility**: The event stream alone is sufficient to visually reconstruct cursor paths, drag-and-drop animations, razor splits, caption stamping, and track modifications at 60 FPS without querying live media files.
3. **Strict Sequencing**: Events contain a monotonic integer `sequence_number` guaranteeing total ordering across concurrent subagents.

---

## 2. Event Ledger Relational Schema (SQLite)

```sql
CREATE TABLE editing_events (
    event_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    sequence_number INTEGER NOT NULL UNIQUE,
    agent_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    agent_color TEXT NOT NULL,
    agent_role TEXT NOT NULL,
    action_type TEXT NOT NULL,
    description TEXT NOT NULL,
    target_track_id TEXT,
    target_track_index INTEGER,
    timeline_time_in REAL,
    timeline_time_out REAL,
    source_asset_id TEXT,
    source_time_in REAL,
    source_time_out REAL,
    before_state_json TEXT,
    after_state_json TEXT,
    visual_payload_json TEXT NOT NULL,
    wall_clock_time REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_project_seq ON editing_events(project_id, sequence_number);
CREATE INDEX idx_events_agent ON editing_events(agent_id);
```

---

## 3. Typed Event JSON Schema (Pydantic / TypeScript Contract)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AgentEditingEvent",
  "type": "object",
  "required": [
    "event_id",
    "project_id",
    "sequence_number",
    "agent",
    "action",
    "description",
    "targets",
    "visual_staging",
    "wall_clock_time"
  ],
  "properties": {
    "event_id": {
      "type": "string",
      "pattern": "^evt_[a-zA-Z0-9_-]+$",
      "description": "Unique cryptographic event identifier"
    },
    "project_id": {
      "type": "string",
      "description": "Project identifier"
    },
    "sequence_number": {
      "type": "integer",
      "minimum": 1,
      "description": "Monotonically increasing sequence index"
    },
    "agent": {
      "type": "object",
      "required": ["agent_id", "name", "role", "color"],
      "properties": {
        "agent_id": { "type": "string", "example": "editor_agent_1" },
        "name": { "type": "string", "example": "Video Editor" },
        "role": { "type": "string", "enum": ["director", "analyst", "editor", "audio", "captions", "colorist", "qc"] },
        "color": { "type": "string", "pattern": "^#[0-9a-fA-F]{6}$", "example": "#00D9FF" }
      }
    },
    "action": {
      "type": "string",
      "enum": [
        "media_drag_drop",
        "clip_split",
        "clip_trim",
        "clip_move",
        "clip_delete",
        "punch_in_apply",
        "transition_add",
        "caption_stamp",
        "color_grade_pulse",
        "audio_level_adjust",
        "qc_verification_scan"
      ]
    },
    "description": {
      "type": "string",
      "description": "Human-readable explanation of why the action was taken"
    },
    "targets": {
      "type": "object",
      "required": ["track_index", "timeline_position"],
      "properties": {
        "track_id": { "type": "string" },
        "track_index": { "type": "integer" },
        "clip_id": { "type": "string" },
        "timeline_position": { "type": "number", "description": "Master timeline time in seconds" },
        "duration": { "type": "number", "description": "Clip or action duration in seconds" },
        "source_asset_id": { "type": "string" },
        "source_range": {
          "type": "array",
          "items": { "type": "number" },
          "minItems": 2,
          "maxItems": 2
        }
      }
    },
    "visual_staging": {
      "type": "object",
      "required": ["start_coords", "target_coords", "motion_curve", "duration_ms"],
      "properties": {
        "start_coords": {
          "type": "object",
          "properties": { "x": { "type": "number" }, "y": { "type": "number" } }
        },
        "target_coords": {
          "type": "object",
          "properties": { "x": { "type": "number" }, "y": { "type": "number" } }
        },
        "motion_curve": {
          "type": "string",
          "enum": ["ease_in_out", "spring", "linear", "snap"]
        },
        "duration_ms": { "type": "number", "default": 600 },
        "cursor_tool_icon": {
          "type": "string",
          "enum": ["pointer", "grab", "razor", "trim_left", "trim_right", "text_stamp", "fader", "eyedropper", "inspect"]
        },
        "haptic_visual": {
          "type": "string",
          "enum": ["none", "slice_particle", "glow_pulse", "ripple", "snap_shadow"]
        }
      }
    },
    "wall_clock_time": {
      "type": "number",
      "description": "Epoch timestamp in seconds when the action occurred"
    }
  }
}
```

---

## 4. Replay State Synthesizer Algorithm

The Replay engine reconstructs the visual scene without reading media frames:
1. **Clock Translation**: The historical interval between events $[T_k, T_{k+1}]$ is mapped to replay playback time: $\Delta t_{\text{replay}} = \frac{T_{k+1} - T_k}{\text{Speed Multiplier}}$.
2. **Bezier Path Generation**: Smooth 3-point quadratic Bezier curves are calculated between `start_coords` and `target_coords`.
3. **Concurrent Overlap**: When multiple events share overlapping wall-clock time intervals, their cursors and animations are rendered simultaneously.
4. **Instant Restart**: The animation stage resets all track DOM elements to state at $t=0$ and restarts the Framer Motion timeline without reload delay.

