"""Loopback-only read API for L07. Not reachable from a cloud agent."""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from urllib.parse import unquote, urlparse

from workshop import ToolInputError, get_stock


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            code, payload = 200, {"status": "ok", "synthetic": True}
        elif path.startswith("/inventory/") and path.count("/") == 2:
            try:
                code, payload = 200, get_stock(unquote(path.removeprefix("/inventory/")))
            except ToolInputError as exc:
                code, payload = 404, {"error": str(exc)}
        else:
            code, payload = 404, {"error": "Unknown route"}
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Use a port between 1024 and 65535.")
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        print(f"Synthetic read-only API: http://127.0.0.1:{args.port} (Ctrl+C to stop)", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
