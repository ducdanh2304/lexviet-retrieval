"""Public-safe artifact and submission validators."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_submission(path: str | Path, expected_queries: int | None = None):
    """Validate a JSON file or ZIP containing exactly `submission.json`."""
    path = Path(path)
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            if archive.namelist() != ["submission.json"]:
                raise ValueError("ZIP must contain only submission.json")
            payload = json.loads(archive.read("submission.json"))
    else:
        payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("submission root must be a JSON object")
    if expected_queries is not None and len(payload) != expected_queries:
        raise ValueError(f"expected {expected_queries} queries, got {len(payload)}")
    for qid, row in payload.items():
        answers = row.get("answer") if isinstance(row, dict) else None
        if not isinstance(qid, str) or not isinstance(answers, list):
            raise ValueError(f"invalid row for query {qid!r}")
        if len(answers) != 5 or len(set(map(str, answers))) != 5:
            raise ValueError(f"query {qid!r} must contain five unique documents")
    return {"queries": len(payload), "valid": True, "sha256": sha256(path)}
