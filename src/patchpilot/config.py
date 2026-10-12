"""Configuration management for PatchPilot AI.
Loads settings from environment variables and provides structured runtime config.
"""

import hashlib
import hmac
import os
import secrets
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

load_dotenv()


def _env_str(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (ValueError, TypeError):
        return default


class PatchPilotConfig(BaseModel):
    # Observability (Neatlogs)
    neatlogs_api_key: str = Field(
        default_factory=lambda: os.getenv("NEATLOGS_API_KEY", ""),
        description="Neatlogs Project API key from NEATLOGS_API_KEY",
    )
    neatlogs_project_id: str = Field(
        default_factory=lambda: os.getenv("NEATLOGS_PROJECT_ID", ""),
        description="Optional Neatlogs project UUID",
    )
    neatlogs_ingest_url: str = Field(
        default_factory=lambda: os.getenv(
            "NEATLOGS_INGEST_URL", "https://ingest.neatlogs.com/v1/trace"
        ),
        description="Ingest endpoint",
    )

    # LLM Settings
    openai_api_key: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", ""),
        description="OpenAI API key",
    )
    anthropic_api_key: str = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""),
        description="Anthropic API key",
    )
    gemini_api_key: str = Field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", ""),
        description="Google Gemini API key",
    )
    model: str = Field(
        default_factory=lambda: os.getenv("PATCHPILOT_MODEL", "gpt-4o"),
        description="Default LLM model",
    )

    # GitHub Settings
    github_token: str = Field(
        default_factory=lambda: os.getenv("GITHUB_TOKEN", ""),
        description="GitHub personal access token",
    )

    # Crustdata Settings
    crustdata_api_key: str = Field(
        default_factory=lambda: os.getenv("CRUSTDATA_API_KEY", ""),
        description="Crustdata API token",
    )

    # Execution & Recovery Budgets
    max_attempts: int = Field(
        default_factory=lambda: _env_int("PATCHPILOT_MAX_ATTEMPTS", 3),
        description="Maximum recovery attempts before declaring unrecoverable",
    )
    execution_timeout_seconds: int = Field(
        default_factory=lambda: _env_int("PATCHPILOT_TIMEOUT_SECONDS", 60),
        description="Timeout per test run command in seconds",
    )
    checkpoint_db_path: Path = Field(
        default_factory=lambda: Path(
            os.getenv("PATCHPILOT_CHECKPOINT_DB", ".patchpilot_state.db")
        ),
        description="SQLite database path for run checkpoints",
    )

    # API security hardening
    api_token: str = Field(
        default_factory=lambda: os.getenv("PATCHPILOT_API_TOKEN", ""),
        description="Legacy single bearer token (back-compat). Prefer PATCHPILOT_API_TOKENS.",
    )
    api_tokens: str = Field(
        default_factory=lambda: os.getenv("PATCHPILOT_API_TOKENS", ""),
        description="Comma-separated 'tenant_id:token' pairs for per-tenant isolation. "
        "When set, every /api/* request is scoped to its tenant.",
    )
    token_encryption_key: str = Field(
        default_factory=lambda: os.getenv("PATCHPILOT_TOKEN_KEY", ""),
        description="Fernet key (base64) used to encrypt stored GitHub tokens. "
        "If empty, tokens are stored plaintext with a startup warning.",
    )
    max_concurrent_repairs: int = Field(
        default_factory=lambda: _env_int("PATCHPILOT_MAX_REPAIRS", 2),
        description="Maximum concurrent background repair jobs",
    )
    cors_allow_origin: str = Field(
        default_factory=lambda: os.getenv("PATCHPILOT_CORS_ORIGIN", ""),
        description="Value for Access-Control-Allow-Origin. Empty = same-origin only.",
    )
    rate_limit_per_minute: int = Field(
        default_factory=lambda: _env_int("PATCHPILOT_RATE_LIMIT", 120),
        description="Max requests per minute per client IP (API routes)",
    )
    require_tls: bool = Field(
        default_factory=lambda: os.getenv("PATCHPILOT_REQUIRE_TLS", "").lower() in ("1", "true", "yes"),
        description="Reject plain-HTTP /api/* requests unless X-Forwarded-Proto: https",
    )
    trust_proxy_headers: bool = Field(
        default_factory=lambda: os.getenv("PATCHPILOT_TRUST_PROXY", "").lower() in ("1", "true", "yes"),
        description="Honor X-Forwarded-For/Proto from reverse proxy (set only behind one)",
    )

    @validator("max_attempts")
    @classmethod
    def _validate_attempts(cls, v: int) -> int:
        if v < 1:
            raise ValueError("max_attempts must be >= 1")
        if v > 10:
            raise ValueError("max_attempts must be <= 10")
        return v

    @validator("execution_timeout_seconds")
    @classmethod
    def _validate_timeout(cls, v: int) -> int:
        if v < 5:
            raise ValueError("execution_timeout_seconds must be >= 5")
        if v > 600:
            raise ValueError("execution_timeout_seconds must be <= 600")
        return v

    @validator("max_concurrent_repairs")
    @classmethod
    def _validate_repairs(cls, v: int) -> int:
        if v < 1:
            raise ValueError("max_concurrent_repairs must be >= 1")
        if v > 8:
            raise ValueError("max_concurrent_repairs must be <= 8")
        return v


# ---------------------------------------------------------------------------
# API bearer-token helpers (timing-safe compare, hashed storage)
# ---------------------------------------------------------------------------

# tenant_id -> bearer token, parsed from PATCHPILOT_API_TOKENS="t1:tok1,t2:tok2"
def parse_api_tokens(raw: str) -> Dict[str, str]:
    tenants: Dict[str, str] = {}
    for pair in (raw or "").split(","):
        pair = pair.strip()
        if not pair or ":" not in pair:
            continue
        tid, _, tok = pair.partition(":")
        tid, tok = tid.strip(), tok.strip()
        if tid and tok and len(tid) <= 64 and len(tok) <= 256:
            tenants[tid] = tok
    return tenants

def hash_api_token(token: str) -> str:
    """SHA-256 hex digest of an API token (for logging/comparison)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_api_token(provided: str, expected: str) -> bool:
    """Constant-time bearer-token comparison."""
    if not provided or not expected:
        return False
    return hmac.compare_digest(provided.encode("utf-8"), expected.encode("utf-8"))


def ensure_api_token(config_obj: "PatchPilotConfig") -> str:
    """Return the configured token, generating+pinning an ephemeral one if unset."""
    if config_obj.api_token:
        return config_obj.api_token
    generated = secrets.token_urlsafe(32)
    config_obj.api_token = generated
    return generated


def resolve_tenant(provided: str, config_obj: "PatchPilotConfig") -> Optional[str]:
    """Map a bearer token to its tenant id (constant-time). None if invalid."""
    tenants = parse_api_tokens(config_obj.api_tokens)
    if tenants:
        for tid, tok in tenants.items():
            if hmac.compare_digest(provided.encode("utf-8"), tok.encode("utf-8")):
                return tid
        return None
    # Back-compat single-token mode: one implicit tenant "default".
    if config_obj.api_token and hmac.compare_digest(
        provided.encode("utf-8"), config_obj.api_token.encode("utf-8")
    ):
        return "default"
    return None


class SlidingWindowRateLimiter:
    """Thread-safe per-key sliding-window limiter (in-memory)."""

    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max(1, max_requests)
        self.window = max(1, window_seconds)
        self._lock = threading.Lock()
        self._hits: Dict[str, List[float]] = {}

    def allow(self, key: str, now: Optional[float] = None) -> bool:
        now = time.time() if now is None else now
        cutoff = now - self.window
        with self._lock:
            hits = [t for t in self._hits.get(key, []) if t > cutoff]
            if len(hits) >= self.max_requests:
                self._hits[key] = hits
                return False
            hits.append(now)
            self._hits[key] = hits
            return True


# Global default configuration instance
config = PatchPilotConfig()
