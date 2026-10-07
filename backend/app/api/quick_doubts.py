from fastapi import APIRouter
from app.schemas.quick_doubts import QuickDoubtsRequest, QuickDoubtsResponse
from app.services.quick_doubts_service import generate_quick_doubt_answer

router = APIRouter()

@router.post("", response_model=QuickDoubtsResponse)
async def ask_quick_doubt(request: QuickDoubtsRequest):
    try:
        answer = await generate_quick_doubt_answer(request.message)
        return QuickDoubtsResponse(status="AVAILABLE", answer=answer)
    except ValueError as e:
        return QuickDoubtsResponse(status="ERROR", message="Quick Doubts is temporarily unavailable.")
    except Exception as e:
        return QuickDoubtsResponse(status="ERROR", message="Quick Doubts is temporarily unavailable.")
