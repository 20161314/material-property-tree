"""Resolve input paths while keeping release pins inside the project root."""

from __future__ import annotations

from pathlib import Path


def resolve_project_input(root: Path, relative_path: str) -> Path | None:
    try:
        candidate_path = Path(relative_path)
        if candidate_path.is_absolute():
            return None
        resolved_root = root.resolve()
        resolved_candidate = (resolved_root / candidate_path).resolve()
        resolved_candidate.relative_to(resolved_root)
    except (OSError, RuntimeError, TypeError, ValueError):
        return None
    return resolved_candidate
