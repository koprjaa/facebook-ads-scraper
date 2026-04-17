"""Configuration — Settings dataclass loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as e:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from e


@dataclass
class Settings:
    """All runtime configuration for the scraper. Use `Settings.from_env()` to load from `.env`."""

    access_token: str = ""
    ad_account_id: str = ""
    limit: int = 100
    output_file: Path = field(default_factory=lambda: Path("processed-ads.json"))
    log_level: str = "INFO"
    timeout: int = 30
    api_version: str = "v20.0"

    def validate(self) -> None:
        """Raise ValueError for any missing or malformed config."""
        if not self.access_token:
            raise ValueError("FACEBOOK_ACCESS_TOKEN environment variable is required")
        if not self.ad_account_id:
            raise ValueError("FACEBOOK_AD_ACCOUNT_ID environment variable is required")
        if not self.ad_account_id.startswith("act_"):
            raise ValueError("FACEBOOK_AD_ACCOUNT_ID must start with 'act_'")
        if self.limit <= 0:
            raise ValueError("FACEBOOK_ADS_LIMIT must be a positive integer")
        if self.timeout <= 0:
            raise ValueError("FACEBOOK_ADS_TIMEOUT must be a positive integer")
        if self.log_level.upper() not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError(
                f"FACEBOOK_ADS_LOG_LEVEL must be one of DEBUG/INFO/WARNING/ERROR/CRITICAL"
                f", got {self.log_level!r}"
            )

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            access_token=os.getenv("FACEBOOK_ACCESS_TOKEN", ""),
            ad_account_id=os.getenv("FACEBOOK_AD_ACCOUNT_ID", ""),
            limit=_int_env("FACEBOOK_ADS_LIMIT", 100),
            output_file=Path(os.getenv("FACEBOOK_ADS_OUTPUT_FILE", "processed-ads.json")),
            log_level=os.getenv("FACEBOOK_ADS_LOG_LEVEL", "INFO"),
            timeout=_int_env("FACEBOOK_ADS_TIMEOUT", 30),
        )
