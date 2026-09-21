from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class MessageResponse(BaseModel):
    message: str

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int

class ErrorResponse(BaseModel):
    error: str
    error_code: str
    detail: Optional[str] = None
