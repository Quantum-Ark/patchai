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
    neatlogs_api_key: str = Field(
        default_factory=lambda: os.getenv("NEATLOGS_API_KEY", ""),
        description="Neatlogs Project API key from NEATLOGS_API_KEY"
    )
    neatlogs_project_id: str = Field(
        default_factory=lambda: os.getenv("NEATLOGS_PROJECT_ID", ""),
        description="Optional Neatlogs project UUID"
    )
    neatlogs_ingest_url: str = Field(
        default=os.getenv("NEATLOGS_INGEST_URL", "https://ingest.neatlogs.com/v1/trace"),
        description="Ingest endpoint"
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

    # Crustdata Settings
    crustdata_api_key: str = Field(
        default_factory=lambda: os.getenv("CRUSTDATA_API_KEY", ""),
        description="Crustdata API token"
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
