from fastapi import APIRouter, Request, status, HTTPException
from app.schemas.response import APIResponse

router = APIRouter(tags=["Health Check"])

@router.get("/health", response_model=APIResponse)
async def health_check(request: Request):
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Hệ thống đang hoạt động bình thường",
        data={
            "status": status.HTTP_200_OK, 
            "service": "Event Management API"
        },
        errors=None,
        path=request.url.path
    )