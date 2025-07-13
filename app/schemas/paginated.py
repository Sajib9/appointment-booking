from pydantic import BaseModel
from typing import List, Generic, TypeVar, Optional
from pydantic.generics import GenericModel

T = TypeVar("T")

class PaginatedResponse(GenericModel, Generic[T]):
    data: List[T]
    total: int
    page: int
    limit: int
    total_pages: int
