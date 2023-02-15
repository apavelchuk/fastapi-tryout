from pydantic import BaseModel
from typing import List, Any, Optional


class ApiListResponse(BaseModel):
    count: int
    results: List[Any]
    next: Optional[str]
    previous: Optional[str]
