from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取项目根目录的绝对路径
ROOT_DIR = Path(__file__).parent.parent.parent.resolve()

__all__ = ["config"]


class EnvConfig(BaseSettings):
    # 仅保留 .env.example 中定义的基础配置项
    debug: bool = Field(default=True, description="启用调试模式")
    log_level: str = Field(
        default="DEBUG", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )
    log_dir: str | None = Field(
        default="", description="日志输出目录（JSON格式），如未指定则仅输出到控制台"
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


# 创建全局配置实例
config: EnvConfig = EnvConfig()
