from typing import TypeVar, Generic
from pydantic import Field, BaseModel

T = TypeVar("T", bound=BaseModel | None)


class EmptyModel(BaseModel):
    """空响应模型，用于不需要返回数据的接口"""

    pass


_EmptyModel = EmptyModel  # 保持向后兼容


def _empty() -> BaseModel:
    """返回空 BaseModel 实例，供 default_factory 使用。"""
    return EmptyModel()


# 导出 EmptyModel 作为 EmptyResponse，以便在其他模块中使用
EmptyResponse = EmptyModel


class ResponseDto(BaseModel, Generic[T]):
    """响应数据传输对象"""

    err_code: int = Field(description="错误码，0表示正常，其他表示错误")
    err_msg: str = Field(description="错误消息")

    data: T | None = Field(
        default=None, description="数据，对应具体业务模型；默认为空对象"
    )
