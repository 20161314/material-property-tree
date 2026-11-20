"""Parse the one authoritative release ID from a release pointer file."""

from __future__ import annotations

import re
from pathlib import Path


_POINTER_ID = re.compile(
    r"release\s*[：:]\s*`?([A-Za-z0-9][A-Za-z0-9_.-]{3,})`?"
    r"|release\s+`([A-Za-z0-9][A-Za-z0-9_.-]{3,})`",
    re.IGNORECASE,
)


def parse_release_pointer(path: Path) -> str | None:
    """Return an ID only when the pointer contains exactly one recognized ID."""
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    matches = list(_POINTER_ID.finditer(text))
    if len(matches) != 1:
        return None
    return matches[0].group(1) or matches[0].group(2)
