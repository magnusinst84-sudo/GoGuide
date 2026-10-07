from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Evidence(BaseModel):
    source: str
    value: str
    confidence: Optional[str] = None
    timestamp: Optional[str] = None

class LLMContext(BaseModel):
    user_profile: Dict[str, Any] = Field(default_factory=dict)
    user_message: str = ""
    deterministic_results: Dict[str, Any] = Field(default_factory=dict)
    retrieved_documents: List[Dict[str, Any]] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    provenance: List[Evidence] = Field(default_factory=list)

class LLMRequest(BaseModel):
    prompt: str
    context: LLMContext

class LLMResponse(BaseModel):
    response_text: str
    generated_at: str
    model: str