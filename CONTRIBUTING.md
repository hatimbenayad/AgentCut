# Contributing to AgentCut

Thank you for your interest in contributing to **AgentCut**!

AgentCut is developed under strict engineering standards: **AI-DLC (AI-Driven Development Lifecycle)** and **SDD (Spec-Driven Development)**.

---

## 1. Non-Negotiable Development Rules

1. **Specification First:** Before writing code for any feature, write or update its specification under `/docs/specs/`. No code should be merged without approved acceptance criteria.
2. **Architecture Decision Records (ADRs):** Any major technology choice or architectural divergence must be documented as an ADR in [`docs/architecture/architecture-decisions.md`](docs/architecture/architecture-decisions.md).
3. **No Fakes or Mock Placeholders in Production Modules:** Never mark a requirement as complete merely because its interface exists. A simulated progress bar is not rendering; a placeholder string is not transcription.
4. **Source Footage Immutability:** Never write code that opens user source media in write or append mode. Edits are virtual clips mapped to timestamps.
5. **Deterministic Replay Guarantee:** Replay animations must reflect real recorded events logged to the SQLite event ledger. Never invent randomized cursor animations.
6. **VRAM Memory Safety:** The system is optimized for 6GB laptop GPUs. Heavy neural models must follow sequential load-infer-unload lifecycles with explicit CUDA garbage collection.

---

## 2. Branching & Commit Conventions

- `feat/`: New feature or capability backed by an SDD specification.
- `fix/`: Bug fix with regression test.
- `spec/`: Documentation, requirements, or architecture specification.
- `refactor/`: Code reorganization without functional change.
- `ci/`: Workflows and automation.

### Commit Format
```text
<type>(<scope>): <short description>

[optional body explaining context]
[optional issue reference, e.g. Fixes #12]
```

---

## 3. Pull Request Guidelines

1. Fork the repo and create your branch from `main`.
2. Follow the SDD checklist in [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md).
3. Run all tests locally before submitting:
   ```bash
   pytest tests/
   python experiments/timeline_mlt/test_timeline_compile.py
   ```
4. Update [`docs/implementation/progress.md`](docs/implementation/progress.md) to record the status transition.
