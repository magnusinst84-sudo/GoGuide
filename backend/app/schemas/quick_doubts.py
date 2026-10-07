from pydantic import BaseModel, Field, constr
from typing import Optional

class QuickDoubtsRequest(BaseModel):
    message: constr(strip_whitespace=True, min_length=1, max_length=2000)

class QuickDoubtsResponse(BaseModel):
    status: str
    answer: Optional[str] = None
    message: Optional[str] = None
