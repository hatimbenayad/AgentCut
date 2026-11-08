"""
Setup GitHub Milestones, Labels, and Issues for AgentCut
"""

import os
import json
import urllib.request
import urllib.error
import time

TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "hatimbenayad/AgentCut"
BASE_URL = f"https://api.github.com/repos/{REPO}"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "AgentCut-Setup-Script"
}

def api_call(path, method="GET", payload=None):
    url = f"{BASE_URL}/{path}"
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        # Ignore already exists errors
        if e.code == 422:
            try:
                err_json = json.loads(error_body)
                print(f"Notice ({path}): {err_json.get('message', error_body)}")
                return None
            except:
                pass
        print(f"HTTP Error {e.code} on {path}: {error_body}")
        return None

def setup_labels():
    print("\n--- Setting up Labels ---")
    labels = [
        {"name": "architecture", "color": "0052cc", "description": "System architecture and ADRs"},
        {"name": "spec", "color": "0e8a16", "description": "Spec-Driven Development specifications"},
        {"name": "video-intelligence", "color": "d93f0b", "description": "VAD, Whisper STT, OCR, Scene detection"},
        {"name": "timeline-engine", "color": "1d76db", "description": "Canonical timeline & MLT XML generation"},
        {"name": "mcp-server", "color": "5319e7", "description": "Model Context Protocol tool interfaces"},
        {"name": "multi-agent", "color": "b60205", "description": "Agent roles & interval concurrency locking"},
        {"name": "replay-studio", "color": "fbca04", "description": "Cinematic multi-cursor replay experience"},
        {"name": "rendering", "color": "c2e0c6", "description": "Dual-engine rendering (melt + FFmpeg)"},
        {"name": "desktop-ui", "color": "bfdadc", "description": "Electron & React 18 desktop application"},
        {"name": "milestone-epic", "color": "7057ff", "description": "Primary roadmap milestone epic"}
    ]
    for lbl in labels:
        res = api_call("labels", method="POST", payload=lbl)
        if res:
            print(f"✔ Label created: {lbl['name']}")
        time.sleep(0.2)

def setup_milestones():
    print("\n--- Setting up Milestones ---")
    milestones_data = [
        {"title": "M1: Inception, Research & Architecture Specs", "description": "Research, hardware feasibility, ADRs, SDD specifications, and empirical validation.", "state": "closed"},
        {"title": "M2: End-to-End Vertical Slice", "description": "Ingest, analyze, canonical timeline edits, dual-engine render, event ledger, and replay prototype.", "state": "open"},
        {"title": "M3: Deepened Intelligence & Previews", "description": "Full pause classifier, temporal OCR tracking, diarization fallback, proxy previews.", "state": "open"},
        {"title": "M4: Production FastMCP Server", "description": "~20 high-leverage typed MCP tools with stdio and SSE transports.", "state": "open"},
        {"title": "M5: Multi-Agent Concurrency", "description": "7 specialized agent roles, track-interval optimistic locking, transaction manager.", "state": "open"},
        {"title": "M6: Desktop Studio UI", "description": "Dark-themed NLE UI (Media Bin, Player, Multitrack Canvas, Review Editor).", "state": "open"},
        {"title": "M7: Cinematic Replay Studio", "description": "Framer Motion 60 FPS multi-cursor collaborative replay studio.", "state": "open"},
        {"title": "M8: DoD Verification & Packaging", "description": "15-step DoD workflow validation, stress testing, Windows NSIS packaging.", "state": "open"}
    ]
    milestone_map = {}
    for ms in milestones_data:
        res = api_call("milestones", method="POST", payload={"title": ms["title"], "description": ms["description"]})
        if res:
            milestone_id = res["number"]
            milestone_map[ms["title"]] = milestone_id
            print(f"✔ Milestone created #{milestone_id}: {ms['title']}")
            if ms["state"] == "closed":
                api_call(f"milestones/{milestone_id}", method="PATCH", payload={"state": "closed"})
        time.sleep(0.3)
    return milestone_map

def setup_issues(milestone_map):
    print("\n--- Creating Milestone Epic Issues ---")
    issues = [
        {
            "title": "[Epic] Milestone 1: AI-DLC Inception, Architecture Specifications & Hardware Feasibility",
            "milestone": milestone_map.get("M1: Inception, Research & Architecture Specs"),
            "labels": ["milestone-epic", "architecture", "spec"],
            "state": "closed",
            "body": """## Milestone 1: Inception, Research & Architecture Specifications

### Summary
Complete initial research, architectural design, ADR formulation, and empirical benchmarks on target hardware.

### Deliverables Completed
- [x] Host environment & GPU VRAM audit (Windows 11, Ryzen 7 7435HS, RTX 4050 6GB VRAM, Python 3.13, FFmpeg 8.0)
- [x] Kdenlive & MLT project format research (`dev-docs/fileformat.md`)
- [x] Technical evaluation of `Jemo69/kdenlive-mcp` ([evaluation-kdenlive-mcp.md](docs/architecture/evaluation-kdenlive-mcp.md))
- [x] ADR-001 through ADR-013 documented in [docs/architecture/architecture-decisions.md](docs/architecture/architecture-decisions.md)
- [x] Empirical S2 Timeline experiment: Canonical Timeline Model compiled to `.kdenlive` XML and rendered to verified 6.00s MP4 in 0.58s
- [x] Empirical S6 Model compatibility verification: RapidOCR (606ms), PySceneDetect (0.60s), faster-whisper (0.48s with `av<14`)
- [x] Replay Event Schema specified in [docs/specs/activity-replay/event-schema.md](docs/specs/activity-replay/event-schema.md)
- [x] Complete documentation package (20 files across `/docs`)
"""
        },
        {
            "title": "[Epic] Milestone 2: End-to-End Vertical Slice",
            "milestone": milestone_map.get("M2: End-to-End Vertical Slice"),
            "labels": ["milestone-epic", "video-intelligence", "timeline-engine", "rendering"],
            "state": "open",
            "body": """## Milestone 2: End-to-End Vertical Slice

### Goal
Deliver a fully functional vertical slice executing the complete editing loop from raw footage to rendered MP4 and animated replay.

### Tasks
- [ ] Implement audio extraction & 16kHz mono conversion via FFmpeg (`agentcut/intelligence/audio.py`)
- [ ] Implement Silero VAD pause detection and acoustic categorization (`agentcut/intelligence/vad.py`)
- [ ] Implement `faster-whisper` transcription with word-level timestamps (`agentcut/intelligence/transcribe.py`)
- [ ] Implement `PySceneDetect` scene cut analysis (`agentcut/intelligence/scene.py`)
- [ ] Implement Unified Intelligence JSON serializer (`agentcut/intelligence/pipeline.py`)
- [ ] Implement Canonical Timeline Model with non-destructive operations: `add_clip`, `split_clip`, `trim_clip`, `punch_in_jump_cut` (`agentcut/core/timeline.py`)
- [ ] Implement Dual-Engine Renderer compiling to `.kdenlive` MLT XML and FFmpeg filtergraph (`agentcut/render/engine.py`)
- [ ] Implement SQLite event ledger atomically recording operations (`agentcut/core/events.py`)
- [ ] Implement Cinematic Replay prototype animating multi-agent cursors from recorded events
- [ ] Run automated test suite validating the entire vertical slice workflow
"""
        },
        {
            "title": "[Epic] Milestone 3: Deepened Intelligence Pipeline & Proxy Previews",
            "milestone": milestone_map.get("M3: Deepened Intelligence & Previews"),
            "labels": ["milestone-epic", "video-intelligence"],
            "state": "open",
            "body": """## Milestone 3: Deepened Intelligence Pipeline & Proxy Previews

### Goal
Expand intelligence capabilities and build responsive UI preview proxies.

### Tasks
- [ ] Refine 4-class pause taxonomy (micro, conversational, dramatic, dead air)
- [ ] Implement RapidOCR PP-OCRv4 with temporal IoU box tracking & deduplication
- [ ] Implement rule-based linguistic filler word & repetition detector (English & Spanish)
- [ ] Integrate speaker diarization with Hugging Face token and VAD clustering fallback
- [ ] Implement low-resolution proxy video generator for instantaneous UI scrubbing
- [ ] Implement chunked pipeline manager for footage > 10 minutes preserving master timestamps
"""
        },
        {
            "title": "[Epic] Milestone 4: Production FastMCP Server (~20 Coarse Typed Tools)",
            "milestone": milestone_map.get("M4: Production FastMCP Server"),
            "labels": ["milestone-epic", "mcp-server"],
            "state": "open",
            "body": """## Milestone 4: Production FastMCP Server

### Goal
Expose the complete studio capabilities to external AI agents over the Model Context Protocol.

### Tasks
- [ ] Implement FastMCP server with stdio transport (Claude Desktop / CLI) and SSE transport
- [ ] Implement 20 coarse, high-leverage tools with rich typed Pydantic parameters (ADR-010)
- [ ] Implement atomic transaction wrapper and automatic checkpoint rollback
- [ ] Enforce filesystem sandboxing and path traversal validation
- [ ] Build automated MCP client test harness simulating agent workflows
"""
        },
        {
            "title": "[Epic] Milestone 5: Multi-Agent Orchestration & Concurrency Locking",
            "milestone": milestone_map.get("M5: Multi-Agent Concurrency"),
            "labels": ["milestone-epic", "multi-agent"],
            "state": "open",
            "body": """## Milestone 5: Multi-Agent Orchestration & Concurrency Locking

### Goal
Coordinate 7 specialized autonomous agent roles working concurrently on a single project.

### Tasks
- [ ] Define agent roles (Director, Analyst, Editor, Audio Engineer, Caption Designer, Colorist, QC)
- [ ] Implement track-interval optimistic locking (`agentcut/orchestration/locks.py`)
- [ ] Implement conflict detection and lease expiration
- [ ] Connect agent operations to single authoritative SQLite project state (ADR-011)
- [ ] Verify multi-agent coordination without data corruption
"""
        },
        {
            "title": "[Epic] Milestone 6: Desktop NLE Studio Interface (Electron + React 18)",
            "milestone": milestone_map.get("M6: Desktop Studio UI"),
            "labels": ["milestone-epic", "desktop-ui"],
            "state": "open",
            "body": """## Milestone 6: Desktop NLE Studio Interface

### Goal
Deliver a dark-themed, professional post-production desktop environment.

### Tasks
- [ ] Set up Electron 34+ shell with secure context-isolated IPC bridge
- [ ] Build Project Media Bin with thumbnail scrubs and search
- [ ] Build Video Preview Monitor with timecode and playback controls
- [ ] Build Multitrack Timeline Canvas (V1, V2, A1, A2, Captions) with zoomable ruler
- [ ] Build Analysis Review panel with interactive waveform and click-to-seek transcript editor
- [ ] Build Agent Activity Panel showing real-time agent thought logs and interval locks
"""
        },
        {
            "title": "[Epic] Milestone 7: Cinematic Multi-Agent Collaborative Replay Studio",
            "milestone": milestone_map.get("M7: Cinematic Replay Studio"),
            "labels": ["milestone-epic", "replay-studio"],
            "state": "open",
            "body": """## Milestone 7: Cinematic Multi-Agent Collaborative Replay Studio

### Goal
Build the signature 60 FPS Framer Motion collaborative visual replay experience.

### Tasks
- [ ] Implement Replay Visual Interpreter synthesizing continuous motion paths from SQLite ledger
- [ ] Build multi-color animated agent cursors (Cyan, Purple, Yellow, Green, Red) with badges
- [ ] Implement animated timeline manipulations (media bin drags, razor blade slices, caption stamps)
- [ ] Build replay playback controls (Play, Pause, Speed 0.5x, 1x, 2x, 4x, scrubber, restart)
- [ ] Verify 100% deterministic playback and visual sandboxing (zero project mutations)
"""
        },
        {
            "title": "[Epic] Milestone 8: End-to-End DoD Integration, Benchmarks & Packaging",
            "milestone": milestone_map.get("M8: DoD Verification & Packaging"),
            "labels": ["milestone-epic"],
            "state": "open",
            "body": """## Milestone 8: End-to-End DoD Integration, Benchmarks & Packaging

### Goal
Validate the complete 15-step Definition of Done workflow and package for Windows distribution.

### Tasks
- [ ] Validate full 15-step Definition of Done workflow end-to-end
- [ ] Stress-test long footage (30+ minutes) and multi-lingual recordings (English/Spanish)
- [ ] Validate native Kdenlive project loading in desktop Kdenlive 23.x/24.x
- [ ] Package Windows standalone executable & NSIS installer via Electron Builder
- [ ] Freeze Python backend into standalone sidecar binary
"""
        }
    ]

    for issue in issues:
        payload = {
            "title": issue["title"],
            "body": issue["body"],
            "labels": issue["labels"]
        }
        if issue["milestone"]:
            payload["milestone"] = issue["milestone"]
        
        res = api_call("issues", method="POST", payload=payload)
        if res:
            issue_num = res["number"]
            print(f"✔ Issue #{issue_num} created: {issue['title']}")
            if issue.get("state") == "closed":
                api_call(f"issues/{issue_num}", method="PATCH", payload={"state": "closed"})
        time.sleep(0.5)

if __name__ == "__main__":
    setup_labels()
    m_map = setup_milestones()
    setup_issues(m_map)
    print("\n=======================================================")
    print("GitHub Labels, Milestones, and Milestone Epics configured successfully!")
