from typing import TypeVar, Generic
from pydantic import Field, BaseModel

T = TypeVar("T", bound=BaseModel | None)


class EmptyModel(BaseModel):
    """Empty response model for endpoints that don't return data"""

    pass


_EmptyModel = EmptyModel  # Keep for backward compatibility


def _empty() -> BaseModel:
    """Return an empty BaseModel instance for use as a default_factory."""
    return EmptyModel()


# Export EmptyModel as EmptyResponse for use in other modules
EmptyResponse = EmptyModel


class ResponseDto(BaseModel, Generic[T]):
    """Response Data Transfer Object"""

    err_code: int = Field(description="Error code: 0 means OK, others indicate errors")
    err_msg: str = Field(description="Error message")

    data: T | None = Field(
        default=None,
        description="Data corresponding to business model; defaults to empty object",
    )
