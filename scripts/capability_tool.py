#!/usr/bin/env python3
"""Manage and build capability manifests."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
BASE_DEFAULT = ROOT / "capabilities" / "base_capabilities.json"
CUSTOM_DEFAULT = ROOT / "capabilities" / "custom_capabilities.json"
FINAL_DEFAULT = ROOT / "capabilities" / "final_capabilities.json"
MERGE_SCRIPT = ROOT / "scripts" / "merge_capabilities.py"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def cmd_add(args: argparse.Namespace) -> None:
    custom = load_json(args.custom)
    custom.setdefault("profile", "my-custom-extensions")
    custom.setdefault("version", 1)
    custom.setdefault("capabilities", [])
    custom.setdefault("enabled", [])
    custom.setdefault("disabled", [])
    custom.setdefault("integrations", [])

    capabilities = custom["capabilities"]
    for item in capabilities:
        if item.get("id") == args.id:
            item.update(
                {
                    "name": args.name,
                    "description": args.description,
                    "category": args.category,
                    "status": args.status,
                }
            )
            save_json(args.custom, custom)
            print(f"Updated capability '{args.id}' in {args.custom}")
            return

    capabilities.append(
        {
            "id": args.id,
            "name": args.name,
            "description": args.description,
            "category": args.category,
            "status": args.status,
        }
    )
    save_json(args.custom, custom)
    print(f"Added capability '{args.id}' to {args.custom}")


def cmd_build(args: argparse.Namespace) -> None:
    subprocess.run(
        [
            sys.executable,
            str(MERGE_SCRIPT),
            "--base",
            str(args.base),
            "--custom",
            str(args.custom),
            "--out",
            str(args.out),
        ],
        check=True,
    )


def cmd_list(args: argparse.Namespace) -> None:
    data = load_json(args.file)
    capabilities = data.get("capabilities", [])
    if not capabilities:
        print("No capabilities found")
        return
    for cap in sorted(capabilities, key=lambda c: c.get("id", "")):
        print(f"{cap.get('id')}\t{cap.get('status', 'unknown')}\t{cap.get('name')}")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Capability management tool")
    sub = p.add_subparsers(dest="cmd", required=True)

    add = sub.add_parser("add", help="Add or update a capability in custom file")
    add.add_argument("--custom", type=Path, default=CUSTOM_DEFAULT)
    add.add_argument("--id", required=True)
    add.add_argument("--name", required=True)
    add.add_argument("--description", required=True)
    add.add_argument("--category", required=True)
    add.add_argument("--status", choices=["enabled", "disabled"], default="enabled")
    add.set_defaults(func=cmd_add)

    build = sub.add_parser("build", help="Build final capabilities from base + custom")
    build.add_argument("--base", type=Path, default=BASE_DEFAULT)
    build.add_argument("--custom", type=Path, default=CUSTOM_DEFAULT)
    build.add_argument("--out", type=Path, default=FINAL_DEFAULT)
    build.set_defaults(func=cmd_build)

    list_cmd = sub.add_parser("list", help="List capabilities in a file")
    list_cmd.add_argument("--file", type=Path, default=FINAL_DEFAULT)
    list_cmd.set_defaults(func=cmd_list)

    return p


def main() -> None:
    args = parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
