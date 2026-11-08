"""
AgentCut Core: SQLite Database, State Store & Event Ledger
Spec reference: docs/specs/activity-replay/event-schema.md
ADR reference: docs/architecture/architecture-decisions.md (ADR-007, ADR-011)
"""

import sqlite3
import json
import os
import time
from typing import List, Dict, Any, Optional
from agentcut.core.timeline import ProjectTimeline
from agentcut.core.events import EditingEvent, VisualStaging, AgentVisualIdentity

class ProjectDatabase:
    """Embedded SQLite database managing project state, locks, and the immutable event ledger."""

    def __init__(self, db_path: str):
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                fps REAL NOT NULL,
                timeline_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS media_assets (
                asset_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                duration REAL NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                fps REAL NOT NULL,
                audio_sample_rate INTEGER,
                waveform_peaks_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS intelligence_records (
                record_id TEXT PRIMARY KEY,
                asset_id TEXT NOT NULL,
                unified_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS interval_locks (
                lock_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                track_id TEXT NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL NOT NULL,
                agent_id TEXT NOT NULL,
                expires_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS editing_events (
                event_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                sequence_number INTEGER NOT NULL,
                agent_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                agent_role TEXT NOT NULL,
                agent_color TEXT NOT NULL,
                action_type TEXT NOT NULL,
                description TEXT NOT NULL,
                target_track_index INTEGER,
                timeline_time_in REAL,
                duration REAL,
                source_asset_id TEXT,
                source_range_json TEXT,
                visual_payload_json TEXT NOT NULL,
                wall_clock_time REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_events_proj_seq ON editing_events(project_id, sequence_number);
            """)

    # --- Project Methods ---
    def save_project(self, timeline: ProjectTimeline):
        timeline_json = timeline.to_json()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            conn.execute("""
            INSERT INTO projects (project_id, name, width, height, fps, timeline_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id) DO UPDATE SET
                name=excluded.name,
                width=excluded.width,
                height=excluded.height,
                fps=excluded.fps,
                timeline_json=excluded.timeline_json,
                updated_at=excluded.updated_at
            """, (
                timeline.project_id,
                timeline.name,
                timeline.profile.width,
                timeline.profile.height,
                timeline.profile.fps,
                timeline_json,
                now
            ))

    def load_project(self, project_id: str) -> Optional[ProjectTimeline]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT timeline_json FROM projects WHERE project_id = ?", (project_id,)).fetchone()
            if row:
                return ProjectTimeline.from_json(row["timeline_json"])
        return None

    # --- Media Assets ---
    def save_media_asset(self, asset_id: str, project_id: str, file_path: str, duration: float,
                         width: int, height: int, fps: float, audio_sample_rate: int, waveform_peaks: List[float]):
        with self._get_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO media_assets 
            (asset_id, project_id, file_path, duration, width, height, fps, audio_sample_rate, waveform_peaks_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                asset_id, project_id, file_path, duration, width, height, fps,
                audio_sample_rate, json.dumps(waveform_peaks)
            ))

    # --- Intelligence Graph ---
    def save_intelligence(self, asset_id: str, unified_dict: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO intelligence_records (record_id, asset_id, unified_json)
            VALUES (?, ?, ?)
            """, (f"intel_{asset_id}", asset_id, json.dumps(unified_dict)))

    def load_intelligence(self, asset_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT unified_json FROM intelligence_records WHERE asset_id = ?", (asset_id,)).fetchone()
            if row:
                return json.loads(row["unified_json"])
        return None

    # --- Event Ledger & Sequence Monotonicity ---
    def append_event(self, event: EditingEvent) -> int:
        """Atomically logs an event to the ledger and assigns the next sequence number."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Calculate next sequence number
            res = cursor.execute("SELECT MAX(sequence_number) FROM editing_events WHERE project_id = ?", (event.project_id,)).fetchone()
            next_seq = (res[0] or 0) + 1
            event.sequence_number = next_seq

            cursor.execute("""
            INSERT INTO editing_events (
                event_id, project_id, sequence_number, agent_id, agent_name, agent_role, agent_color,
                action_type, description, target_track_index, timeline_time_in, duration,
                source_asset_id, source_range_json, visual_payload_json, wall_clock_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.project_id,
                event.sequence_number,
                event.agent.agent_id,
                event.agent.name,
                event.agent.role,
                event.agent.color,
                event.action_type,
                event.description,
                event.target_track_index,
                event.timeline_time_in,
                event.duration,
                event.source_asset_id,
                json.dumps(event.source_range) if event.source_range else None,
                json.dumps(event.visual_staging.__dict__),
                event.wall_clock_time
            ))
            return next_seq

    def get_events(self, project_id: str) -> List[EditingEvent]:
        """Retrieves all events in strict monotonic sequence order."""
        with self._get_connection() as conn:
            rows = conn.execute("""
            SELECT * FROM editing_events 
            WHERE project_id = ? 
            ORDER BY sequence_number ASC
            """, (project_id,)).fetchall()
            
            events = []
            for r in rows:
                vs_dict = json.loads(r["visual_payload_json"])
                events.append(EditingEvent(
                    event_id=r["event_id"],
                    project_id=r["project_id"],
                    sequence_number=r["sequence_number"],
                    agent=AgentVisualIdentity(
                        agent_id=r["agent_id"],
                        name=r["agent_name"],
                        role=r["agent_role"],
                        color=r["agent_color"]
                    ),
                    action_type=r["action_type"],
                    description=r["description"],
                    target_track_index=r["target_track_index"],
                    timeline_time_in=r["timeline_time_in"],
                    duration=r["duration"] or 0.0,
                    source_asset_id=r["source_asset_id"],
                    source_range=json.loads(r["source_range_json"]) if r["source_range_json"] else None,
                    visual_staging=VisualStaging(**vs_dict),
                    wall_clock_time=r["wall_clock_time"]
                ))
            return events

    # --- Interval Concurrency Locking ---
    def acquire_lock(self, project_id: str, track_id: str, start_time: float, end_time: float, agent_id: str, lease_seconds: float = 10.0) -> bool:
        now = time.time()
        expires = now + lease_seconds
        with self._get_connection() as conn:
            # Purge expired locks
            conn.execute("DELETE FROM interval_locks WHERE expires_at < ?", (now,))
            
            # Check for overlapping locks
            conflict = conn.execute("""
            SELECT * FROM interval_locks 
            WHERE project_id = ? AND track_id = ? AND agent_id != ?
            AND NOT (end_time <= ? OR start_time >= ?)
            """, (project_id, track_id, agent_id, start_time, end_time)).fetchone()

            if conflict:
                return False

            lock_id = f"lock_{track_id}_{int(start_time*100)}_{agent_id}"
            conn.execute("""
            INSERT OR REPLACE INTO interval_locks (lock_id, project_id, track_id, start_time, end_time, agent_id, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (lock_id, project_id, track_id, start_time, end_time, agent_id, expires))
            return True

    def release_lock(self, project_id: str, track_id: str, agent_id: str):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM interval_locks WHERE project_id = ? AND track_id = ? AND agent_id = ?",
                         (project_id, track_id, agent_id))

