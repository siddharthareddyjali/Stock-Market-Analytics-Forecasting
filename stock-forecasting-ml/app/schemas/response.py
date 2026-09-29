from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Any | None = None


class HealthResponse(BaseModel):
    status: str
    database: str
    version: str
