from typing import Optional
from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.response import APIResponse
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.schemas.event_staff import EventStaffCreate, EventStaffResponse
from app.services.event import (create_event_ser, 
                                get_events_ser, 
                                get_event_detail_ser, 
                                update_event_ser, 
                                delete_event_ser,
                                add_member_ser,
                                remove_member_ser, 
                                get_members_ser)

router = APIRouter(prefix="/events", tags=["Event Management"])

@router.post("", response_model=APIResponse)
def create_event(
    event: EventCreate, 
    request: Request, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    event = create_event_ser(event, current_user, db)
    return APIResponse(
        status_code=status.HTTP_201_CREATED,
        message="Tạo sự kiện thành công",
        data=EventResponse.model_validate(event),
        errors=None,
        path=request.url.path
    )



@router.get("", response_model=APIResponse)
def list_events(
    request: Request,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = get_events_ser(current_user, search, db, page, limit)
    
    result["items"] = [EventResponse.model_validate(e) for e in result["items"]]
    
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách sự kiện thành công",
        data=result,
        errors=None,
        path=request.url.path
    )

@router.get("/{id}", response_model=APIResponse)
def get_event_detail(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = get_event_detail_ser(id, current_user, db)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Lấy chi tiết sự kiện thành công",
        data=EventResponse.model_validate(event),
        errors=None,
        path=request.url.path
    )

@router.patch("/{id}", response_model=APIResponse)  
def update_event(
    id: int,
    event_in: EventUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_event = update_event_ser(id, event_in, current_user, db)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Cập nhật sự kiện thành công",
        data=EventResponse.model_validate(updated_event),
        errors=None,
        path=request.url.path
    )

@router.delete("/{id}", response_model=APIResponse)
def delete_event(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_event_ser(id, current_user, db)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Xóa sự kiện thành công",
        data=None,
        errors=None,
        path=request.url.path
    )


@router.post("/{id}/members", response_model=APIResponse)
def add_member(
    id: int,
    staff_in: EventStaffCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_staff = add_member_ser(id, staff_in, current_user, db)
    return APIResponse(
        status_code=status.HTTP_201_CREATED,
        message="Thêm thành viên vào sự kiện thành công",
        data=EventStaffResponse.model_validate(new_staff),
        errors=None,
        path=request.url.path
    )

@router.delete("/{id}/members/{user_id}", response_model=APIResponse)
def remove_member(
    id: int,
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    remove_member_ser(id, user_id, current_user, db)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Xóa thành viên khỏi sự kiện thành công",
        data=None,
        errors=None,
        path=request.url.path
    )

@router.get("/{id}/members", response_model=APIResponse)
def get_members(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    members = get_members_ser(id, current_user, db)
    return APIResponse(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách thành viên thành công",
        data=[EventStaffResponse.model_validate(m) for m in members],
        errors=None,
        path=request.url.path
    )