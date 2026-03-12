from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get absolute path of project root directory
ROOT_DIR = Path(__file__).parent.parent.parent.resolve()

__all__ = ["config"]


class EnvConfig(BaseSettings):
    # Only keep basic config items defined in .env.example
    debug: bool = Field(default=True, description="Enable debug mode")
    log_level: str = Field(
        default="DEBUG", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )
    log_dir: str | None = Field(
        default="",
        description="Log output directory (JSON format); if not specified, logs only to console",
    )

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="",
        env_nested_delimiter="__",
        extra="ignore",
        validate_default=True,
        protected_namespaces=("model_", "settings_"),
        # secrets_dir="secrets"
    )


# Create global config instance
config: EnvConfig = EnvConfig()
