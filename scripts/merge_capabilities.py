#!/usr/bin/env python3
"""Merge baseline and custom capability JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Top-level JSON must be an object: {path}")
    return data


def index_caps(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in items:
        cap_id = item.get("id")
        if not cap_id:
            raise ValueError("Every capability must have an 'id'.")
        out[str(cap_id)] = dict(item)
    return out


def merge(base: dict[str, Any], custom: dict[str, Any]) -> dict[str, Any]:
    base_caps = index_caps(base.get("capabilities", []))
    custom_caps = index_caps(custom.get("capabilities", []))

    merged_caps = {**base_caps}
    for cap_id, cap in custom_caps.items():
        if cap_id in merged_caps:
            merged_caps[cap_id].update(cap)
        else:
            merged_caps[cap_id] = cap

    for cap_id in custom.get("enabled", []):
        if cap_id in merged_caps:
            merged_caps[cap_id]["status"] = "enabled"

    for cap_id in custom.get("disabled", []):
        if cap_id in merged_caps:
            merged_caps[cap_id]["status"] = "disabled"

    return {
        "profile": custom.get("profile", "final-capability-profile"),
        "version": max(int(base.get("version", 1)), int(custom.get("version", 1))),
        "capabilities": sorted(merged_caps.values(), key=lambda c: c["id"]),
        "safety": custom.get("safety", base.get("safety", {})),
        "integrations": [
            *(base.get("integrations", []) or []),
            *(custom.get("integrations", []) or []),
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge capability JSON files")
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--custom", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    base = load_json(args.base)
    custom = load_json(args.custom)
    merged = merge(base, custom)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")

    print(f"Wrote merged capabilities to {args.out}")


if __name__ == "__main__":
    main()
