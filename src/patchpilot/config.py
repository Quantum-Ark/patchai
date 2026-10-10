"""
Configuration management for PatchPilot AI.
Loads settings from environment variables and provides structured runtime config.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class PatchPilotConfig(BaseModel):
    # Observability (Neatlogs)
    neatlogs_project_id: str = Field(
        default="b0860223-3c80-445d-a3f1-3002c0643197",
        description="Neatlogs project UUID"
    )
    neatlogs_api_key: str = Field(
        default_factory=lambda: os.getenv("NEATLOGS_API_KEY", ""),
        description="Neatlogs write API key"
    )
    neatlogs_ingest_url: str = Field(
        default="https://ingest.neatlogs.com/v1/trace",
        description="Regional ingest endpoint"
    )

    # LLM Settings
    openai_api_key: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", ""),
        description="OpenAI API key"
    )
    anthropic_api_key: str = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""),
        description="Anthropic API key"
    )
    model: str = Field(
        default_factory=lambda: os.getenv("PATCHPILOT_MODEL", "gpt-4o"),
        description="Default LLM model"
    )

    # GitHub Settings
    github_token: str = Field(
        default_factory=lambda: os.getenv("GITHUB_TOKEN", ""),
        description="GitHub personal access token"
    )

    # Execution & Recovery Budgets
    max_attempts: int = Field(
        default=3,
        description="Maximum recovery attempts before declaring unrecoverable"
    )
    execution_timeout_seconds: int = Field(
        default=60,
        description="Timeout per test run command in seconds"
    )
    checkpoint_db_path: Path = Field(
        default=Path(".patchpilot_state.db"),
        description="SQLite database path for run checkpoints"
    )


# Global default configuration instance
config = PatchPilotConfig()
