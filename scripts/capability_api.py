#!/usr/bin/env python3
"""HTTP API for capability management.

Run this service and call it by URL.
"""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from capability_tool import cmd_add, cmd_build, load_json

ROOT = Path(__file__).resolve().parent.parent
BASE_DEFAULT = ROOT / "capabilities" / "base_capabilities.json"
CUSTOM_DEFAULT = ROOT / "capabilities" / "custom_capabilities.json"
FINAL_DEFAULT = ROOT / "capabilities" / "final_capabilities.json"


class ApiHandler(BaseHTTPRequestHandler):
    base_path: Path = BASE_DEFAULT
    custom_path: Path = CUSTOM_DEFAULT
    final_path: Path = FINAL_DEFAULT

    def _send_json(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length) if content_length else b"{}"
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON body must be an object")
        return data

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json(HTTPStatus.OK, {"status": "ok"})
            return

        if self.path == "/capabilities/base":
            self._send_json(HTTPStatus.OK, load_json(self.base_path))
            return

        if self.path == "/capabilities/custom":
            self._send_json(HTTPStatus.OK, load_json(self.custom_path))
            return

        if self.path == "/capabilities/final":
            self._send_json(HTTPStatus.OK, load_json(self.final_path))
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        try:
            if self.path == "/capabilities/add":
                data = self._read_json()
                missing = [
                    key
                    for key in ("id", "name", "description", "category")
                    if key not in data
                ]
                if missing:
                    self._send_json(
                        HTTPStatus.BAD_REQUEST,
                        {"error": f"Missing fields: {', '.join(missing)}"},
                    )
                    return

                cmd_add(
                    argparse.Namespace(
                        custom=self.custom_path,
                        id=data["id"],
                        name=data["name"],
                        description=data["description"],
                        category=data["category"],
                        status=data.get("status", "enabled"),
                    )
                )
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "message": "Capability added/updated",
                        "custom_file": str(self.custom_path),
                    },
                )
                return

            if self.path == "/build":
                cmd_build(
                    argparse.Namespace(
                        base=self.base_path,
                        custom=self.custom_path,
                        out=self.final_path,
                    )
                )
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "message": "Build complete",
                        "output": str(self.final_path),
                    },
                )
                return

            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
        except Exception as exc:  # handled response for API callers
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})


def main() -> None:
    parser = argparse.ArgumentParser(description="Capability API server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--base", type=Path, default=BASE_DEFAULT)
    parser.add_argument("--custom", type=Path, default=CUSTOM_DEFAULT)
    parser.add_argument("--final", type=Path, default=FINAL_DEFAULT)
    args = parser.parse_args()

    ApiHandler.base_path = args.base
    ApiHandler.custom_path = args.custom
    ApiHandler.final_path = args.final

    server = ThreadingHTTPServer((args.host, args.port), ApiHandler)
    print(f"Serving capability API at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
