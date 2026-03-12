from typing import Any

from pydantic import BaseModel
from src.router.models.response_dto import ResponseDto
from src.config import create_app

# 创建应用实例
app = create_app()


class HealthStatus(BaseModel):
    status: str
    version: str


@app.get("/", response_model=ResponseDto[Any])
async def root() -> ResponseDto[Any]:
    """健康检查接口"""
    return ResponseDto(
        err_code=0,
        err_msg="Perfect! miremo service is running",
        data=None,
    )


@app.get("/health", response_model=ResponseDto[HealthStatus])
async def health_check() -> ResponseDto[HealthStatus]:
    """健康检查接口"""

    health_status = HealthStatus(
        status="healthy",
        version="1.0.0",
    )
    return ResponseDto(
        err_code=0,
        err_msg="ok",
        data=health_status,
    )
