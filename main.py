from __future__ import annotations
import uvicorn

from src.common.env import config  # 从统一的环境配置获取变量

# 仅当 config.debug 为 True 时启用热重载
DEBUG: bool = bool(config.debug)

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
        reload_dirs=["src"] if DEBUG else None,
    )
