from fastapi import APIRouter, Depends, Request, status, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.response import APIResponse
from app.schemas.event_task import EventTaskCreate, EventTaskUpdate, EventTaskResponse
from app.services.event_task import (
    create_task_ser,
    get_event_tasks_ser,
    get_task_detail_ser,
    update_task_ser,
    delete_task_ser
)

router = APIRouter(tags=["Event Tasks Management"])

@router.post("/events/{id}/event-tasks", response_model=APIResponse)
def create_task(
    id: int,
    task_in: EventTaskCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = create_task_ser(id, task_in, current_user, db)
    return APIResponse(
        status_code=status.HTTP_201_CREATED,
        message="Tạo công việc sự kiện thành công",
        data=EventTaskResponse.model_validate(task),
        errors=None,
        path=request.url.path
    )

@router.get("/events/{id}/event-tasks", response_model=APIResponse)
def list_event_tasks(
    id: int,
    request: Request,
    status_filter: Optional[str] = Query(None, alias="status"),
    priority_filter: Optional[str] = Query(None, alias="priority"),
    assignee_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = get_event_tasks_ser(
        event_id=id,
        current_user=current_user,
        db=db,
        status_filter=status_filter,
        priority_filter=priority_filter,
        assignee_id=assignee_id,
        search=search,
        page=page,
        size=size,
        sort_by=sort_by,
        order=order
    )
    result["items"] = [EventTaskResponse.model_validate(t) for t in result["items"]]
    if result["total"] < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Danh sách công việc đang trống"
        )

    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách công việc thành công",
        data=result,
        errors=None,
        path=request.url.path
    )

@router.get("/event-tasks/{id}", response_model=APIResponse)
def get_task_detail(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = get_task_detail_ser(id, current_user, db)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Lấy chi tiết công việc thành công",
        data=EventTaskResponse.model_validate(task),
        errors=None,
        path=request.url.path
    )

@router.patch("/event-tasks/{id}", response_model=APIResponse)
def update_task(
    id: int,
    task_in: EventTaskUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = update_task_ser(id, task_in, current_user, db)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Cập nhật công việc thành công",
        data=EventTaskResponse.model_validate(task),
        errors=None,
        path=request.url.path
    )

@router.delete("/event-tasks/{id}", response_model=APIResponse)
def delete_task(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_task_ser(id, current_user, db)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Xóa công việc thành công",
        data=None,
        errors=None,
        path=request.url.path
    )