from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from src.common.log import get_logger
from src.common.env import config

log = get_logger(__name__)


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""

    app = FastAPI(
        title="Information Assistant API",
        description="API for gathering and processing information from various sources",
        version="1.0.0",
    )

    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 在生产环境中应该设置具体的域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 全局异常处理
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        log.error("FASTAPI: HTTP error", exc_info=exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "err_code": exc.status_code,
                "err_msg": "HTTP 错误",
                "data": exc.detail if config.debug else None,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        log.error("FASTAPI: Request validation error", exc_info=exc)
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "err_code": HTTP_422_UNPROCESSABLE_ENTITY,
                "err_msg": "参数验证错误",
                "data": exc.errors() if config.debug else None,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        log.error("FASTAPI: Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "err_code": HTTP_500_INTERNAL_SERVER_ERROR,
                "err_msg": "内部服务器错误",
                "data": None,
            },
        )

    return app
