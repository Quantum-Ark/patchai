"""
PatchPilot AI Production HTTP & API Server.
Designed for AWS App Runner, ECS Fargate, Kubernetes, and local deployment.
Serves the web workbench interface, provides health probes, and exposes API endpoints.
"""

import os
import sys
import json
import logging
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
from typing import Optional

from patchpilot import __version__
from patchpilot.config import config
from patchpilot.models import Issue
from patchpilot.orchestrator import PatchPilotOrchestrator
from patchpilot.llm.provider import get_llm_provider

logger = logging.getLogger("patchpilot.server")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)


class PatchPilotRequestHandler(SimpleHTTPRequestHandler):
    """
    HTTP Request Handler combining static web asset delivery
    with cloud health probes (/health) and agent API endpoints (/api/*).
    """

    def __init__(self, *args, directory=None, **kwargs):
        if directory is None:
            # Resolve web directory relative to package root
            repo_root = Path(__file__).resolve().parent.parent.parent
            directory = str(repo_root / "web")
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. Cloud Health Probe (/health)
        if path in ("/health", "/healthz", "/ping"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            payload = {
                "status": "healthy",
                "service": "patchpilot-ai",
                "version": __version__,
                "model": config.model,
                "neatlogs_configured": bool(config.neatlogs_api_key),
            }
            self.wfile.write(json.dumps(payload, indent=2).encode("utf-8"))
            return

        # 2. System Status Endpoint (/api/status)
        if path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            status_payload = {
                "version": __version__,
                "neatlogs": {
                    "enabled": bool(config.neatlogs_api_key),
                    "ingest_url": config.neatlogs_ingest_url,
                    "project_id": config.neatlogs_project_id,
                },
                "llm": {
                    "model": config.model,
                    "max_attempts": config.max_attempts,
                    "timeout_seconds": config.execution_timeout_seconds,
                },
                "recovery": {
                    "checkpoint_db": str(config.checkpoint_db_path),
                }
            }
            self.wfile.write(json.dumps(status_payload, indent=2).encode("utf-8"))
            return

        # 3. Fallback to static web files
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Autonomous Repair Trigger (/api/repair)
        if path == "/api/repair":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"

            try:
                data = json.loads(post_body)
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON payload"}).encode("utf-8"))
                return

            issue_title = data.get("title", "AWS Cloud Repair Task")
            issue_body = data.get("body", "Autonomous repair triggered via AWS API")
            provider_override = data.get("provider")

            try:
                llm = get_llm_provider(provider_override)
                issue = Issue(
                    id=f"aws-{os.urandom(4).hex()}",
                    title=issue_title,
                    body=issue_body,
                )
                repo_root = Path(__file__).resolve().parent.parent.parent
                orchestrator = PatchPilotOrchestrator(
                    repo_dir=repo_root,
                    llm_provider=llm
                )
                report = orchestrator.run(issue)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(report.model_dump(), indent=2).encode("utf-8"))
            except Exception as e:
                logger.error(f"Error during repair execution: {e}", exc_info=True)
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def log_message(self, format, *args):
        logger.info("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))


def run_server(host: str = "0.0.0.0", port: int = 8080):
    """Start the production server."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    web_dir = repo_root / "web"
    if not web_dir.exists():
        logger.warning(f"Web directory not found at {web_dir}. Serving from repo root.")
        web_dir = repo_root

    server_address = (host, port)
    httpd = HTTPServer(server_address, PatchPilotRequestHandler)
    logger.info(f"PatchPilot AI Production Server listening on http://{host}:{port}")
    logger.info(f"Health check probe active at http://{host}:{port}/health")
    logger.info(f"Serving web workbench from {web_dir}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    finally:
        httpd.server_close()
        logger.info("Server stopped.")


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg in ("--port", "-p") and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
            elif arg in ("--host", "-h") and i + 1 < len(sys.argv):
                host = sys.argv[i + 1]
    run_server(host=host, port=port)
