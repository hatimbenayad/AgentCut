# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

---

## Security Boundaries & Sandboxing Guarantees

AgentCut executes instructions from external autonomous AI agents via the Model Context Protocol (MCP). To safeguard host machines and user data:

1. **Path Traversal Jail:** All MCP tools canonicalize paths and reject attempts to traverse outside designated project directories.
2. **Immutable Master Footage:** Raw user footage is strictly opened with read-only permissions (`O_RDONLY`). Overwriting source media is prohibited at the kernel and application layer.
3. **No Raw Shell Invocations:** FFmpeg, FFprobe, and MLT `melt` processes are invoked using parameterized argument arrays (`subprocess.run(["ffmpeg", ...])`), preventing shell command injection.
4. **Optimistic Interval Locking:** Concurrent agent writes require leased interval locks, preventing state corruption.

---

## Reporting a Vulnerability

If you discover a security vulnerability in AgentCut:
1. **Do not open a public issue.**
2. Send a detailed report to `hatimbenayad8@gmail.com`.
3. Include reproduction steps, attack surface analysis, and impact assessment.
4. We aim to acknowledge reports within 48 hours and provide patches within 7 days.

