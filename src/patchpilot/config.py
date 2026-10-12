"""Configuration management for PatchPilot AI.
Loads settings from environment variables and provides structured runtime config.
"""

import hashlib
import hmac
import os
import secrets
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
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

    @field_validator("max_attempts")
    @classmethod
    def _validate_attempts(cls, v: int) -> int:
        if v < 1:
            raise ValueError("max_attempts must be >= 1")
        if v > 10:
            raise ValueError("max_attempts must be <= 10")
        return v

    @field_validator("execution_timeout_seconds")
    @classmethod
    def _validate_timeout(cls, v: int) -> int:
        if v < 5:
            raise ValueError("execution_timeout_seconds must be >= 5")
        if v > 600:
            raise ValueError("execution_timeout_seconds must be <= 600")
        return v


# Global default configuration instance
config = PatchPilotConfig()
