from fastapi import APIRouter, HTTPException
from app.schemas.guide import GuideRequest, GuideResponse
from app.services.guide_service import process_guide_request

router = APIRouter()

@router.post("", response_model=GuideResponse)
def guide_endpoint(request: GuideRequest):
    try:
        return process_guide_request(request)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
