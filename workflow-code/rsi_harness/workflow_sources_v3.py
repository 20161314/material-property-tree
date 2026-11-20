"""Explicit manifest adapters and bounded, checksum-verified asset acquisition.

Field maps are supplied by the source adapter; no name or material is inferred.
Only locally authored component records are expanded by this module.
"""
import csv
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import zipfile


def read_records(path, field_map=None):
    """Stream JSON/JSONL/CSV/TSV (optionally gzipped), preserving raw columns."""
    path = Path(path)
    suffixes = path.suffixes
    compressed = bool(suffixes and suffixes[-1] == ".gz")
    suffix = suffixes[-2] if compressed and len(suffixes) > 1 else path.suffix
    opener = gzip.open if compressed else open
    csv.field_size_limit(64 * 1024 * 1024)
    with opener(path, "rt", encoding="utf-8-sig", newline="") as handle:
        if suffix in {".csv", ".tsv"}:
            records = csv.DictReader(handle, delimiter="\t" if suffix == ".tsv" else ",")
        elif suffix == ".jsonl":
            records = (json.loads(line) for line in handle if line.strip())
        elif suffix == ".json":
            records = json.load(handle)
            if not isinstance(records, list):
                raise ValueError("JSON manifest must contain an explicit record array")
        else:
            raise ValueError("Unsupported source manifest format")
        for row in records:
            if not isinstance(row, dict):
                raise ValueError("Manifest row must be an object")
            if field_map is None:
                yield row
            else:
                projected = {target: row[source] for target, source in field_map.items() if source in row}
                projected["source_raw_fields"] = row
                yield projected


def component_records(objects):
    """Expand only supplied source parts; otherwise retain an honest whole fallback."""
    result = []
    for obj in objects:
        object_id = obj["object_id"]
        locator = obj.get("source_locator")
        if not isinstance(locator, str) or not locator.strip():
            raise ValueError("Object source locator required")
        parts = obj.get("source_components", [])
        if not isinstance(parts, list):
            raise ValueError("Source components must be an explicit list")
        if parts:
            for part in parts:
                if part.get("source_authored") is not True or not part.get("source_locator") or not part.get("component_id"):
                    raise ValueError("Component requires source-authored identity and locator")
                if part.get("object_id", object_id) != object_id:
                    raise ValueError("Component belongs to another object")
                result.append(dict(part, object_id=object_id, scope=part.get("scope", "SOURCE_AUTHORED_PART")))
        else:
            result.append({"component_id": object_id + "::WHOLE", "object_id": object_id,
                           "scope": "WHOLE_OBJECT_FALLBACK", "name_zh": "整件（未拆分）",
                           "name_en": "Whole object (not decomposed)", "source_locator": locator})
    identities = [row["component_id"] for row in result]
    if len(identities) != len(set(identities)):
        raise ValueError("Duplicate component identity")
    return result


def verify_payload(path, expected_sha256, format_hint=None):
    path = Path(path)
    result = hashlib.sha256()
    with path.open("rb") as handle:
        prefix = handle.read(512)
        result.update(prefix)
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    actual = result.hexdigest()
    if actual != expected_sha256:
        raise ValueError("Asset SHA mismatch")
    stripped = prefix.lstrip().lower()
    if stripped.startswith((b"<html", b"<!doctype html", b"<?xml", b"<error")):
        raise ValueError("Download is an HTML/XML error, not an asset")
    if format_hint == "glb":
        if prefix[:4] != b"glTF" or len(prefix) < 12:
            raise ValueError("Invalid GLB header")
        import struct
        _, version, length = struct.unpack("<4sII", prefix[:12])
        if version != 2 or length != path.stat().st_size:
            raise ValueError("Invalid GLB version or length")
    if format_hint == "zip":
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                parts = Path(name)
                if parts.is_absolute() or ".." in parts.parts or "\\" in name:
                    raise ValueError("Unsafe archive locator")
            if archive.testzip() is not None:
                raise ValueError("ZIP integrity check failed")
    return {"sha256": actual, "bytes": path.stat().st_size, "verified_payload": True,
            "geometry_deduplication_claimed": False}


def acquire_asset(url, destination, *, expected_sha256, license_or_access, max_bytes=256 * 1024 * 1024, format_hint=None):
    """Download one explicit HTTPS payload; never overwrite a different file."""
    if urlsplit(url).scheme != "https" or not license_or_access:
        raise ValueError("HTTPS official URL and license/access declaration required")
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or any(c not in "0123456789abcdef" for c in expected_sha256):
        raise ValueError("Expected SHA-256 required")
    if type(max_bytes) is not int or not 0 < max_bytes <= 2 * 1024 ** 3:
        raise ValueError("Bounded payload budget required")
    out = Path(destination)
    if out.exists():
        return dict(verify_payload(out, expected_sha256, format_hint), cache_hit=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with urlopen(Request(url, headers={"User-Agent": "RSI-source-verifier/3"}), timeout=30) as response:
            if urlsplit(response.geturl()).scheme != "https":
                raise ValueError("Non-HTTPS redirect blocked")
            declared = response.headers.get("Content-Length")
            if declared and int(declared) > max_bytes:
                raise ValueError("Asset exceeds payload budget")
            with tempfile.NamedTemporaryFile(dir=out.parent, prefix=".rsi-payload-", delete=False) as handle:
                temp = Path(handle.name)
                total = 0
                while True:
                    chunk = response.read(min(1024 * 1024, max_bytes - total + 1))
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        raise ValueError("Asset exceeds payload budget")
                    handle.write(chunk)
        receipt = verify_payload(temp, expected_sha256, format_hint)
        # The verified same-filesystem payload appears atomically. A racing
        # writer cannot overwrite either the source or an existing cache file.
        os.link(temp, out)
        return dict(receipt, cache_hit=False, source_url=url, license_or_access=license_or_access)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
