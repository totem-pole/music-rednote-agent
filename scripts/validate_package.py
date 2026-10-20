#!/usr/bin/env python3
"""Offline structural checks for AFTERTONE album research packages.

Checks are conservative: successful validation is NOT factual verification,
copyright clearance, or a proof that text is original.
"""
import json
import pathlib
import sys


def validate(directory: pathlib.Path) -> list[str]:
    errors = []
    required = ["sources.json", "claim-ledger.json", "research.md", "review.md", "manifest.json"]
    for filename in required:
        if not (directory / filename).is_file():
            errors.append(f"missing {filename}")
    if errors:
        return errors
    try:
        sources = json.loads((directory / "sources.json").read_text(encoding="utf-8"))
        claims = json.loads((directory / "claim-ledger.json").read_text(encoding="utf-8"))
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"invalid data: {exc}"]
    if not isinstance(sources, list) or not sources:
        errors.append("sources.json must be a nonempty list")
        sources = []
    ids = {src.get("id") for src in sources if isinstance(src, dict)}
    for src in sources:
        if not isinstance(src, dict):
            errors.append("source must be an object")
            continue
        for key in ("id", "url", "title", "publisher", "category", "retrieved_at", "access_status"):
            if not src.get(key):
                errors.append(f"source missing {key}")
    if not isinstance(claims, list):
        errors.append("claim-ledger.json must be a list")
        claims = []
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict) or not claim.get("claim"):
            errors.append(f"claim {i} invalid")
            continue
        typ = claim.get("type")
        if typ not in ("FACT", "QUOTE", "INTERPRETATION", "UNVERIFIED"):
            errors.append(f"claim {i} invalid type")
        refs = claim.get("source_ids", [])
        if typ in ("FACT", "QUOTE") and (not refs or any(ref not in ids for ref in refs)):
            errors.append(f"claim {i} needs matching source ids")
    if not isinstance(manifest, dict) or not all(manifest.get(x) for x in ("artist", "album", "edition")):
        errors.append("manifest needs artist, album, edition")
    if not (directory / "review.md").read_text(encoding="utf-8").strip():
        errors.append("review.md empty")
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/validate_package.py research/YYYY-MM-DD/slug")
    problems = validate(pathlib.Path(sys.argv[1]))
    if problems:
        print("\n".join(f"ERROR: {x}" for x in problems))
        raise SystemExit(1)
    print("Structural validation passed. Manual factual, originality and rights review still required.")
