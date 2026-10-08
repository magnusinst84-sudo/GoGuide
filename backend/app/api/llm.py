from fastapi import APIRouter, HTTPException
from app.schemas.llm import LLMRequest, LLMResponse
from app.services.llm_service import process_chat_request

router = APIRouter()

@router.post("/chat", response_model=LLMResponse)
def chat_with_llm(request: LLMRequest):
    try:
        return process_chat_request(request)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")