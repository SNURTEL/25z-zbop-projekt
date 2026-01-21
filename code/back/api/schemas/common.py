"""Common schemas used across the API."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str
