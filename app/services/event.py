from typing import List, Optional

from sqlalchemy.orm import Session, joinedload
from app.schemas.event import EventCreate, EventUpdate
from app.schemas.event_staff import EventStaffCreate
from app.models.event import Event,EventStaff
from app.models.user import User
from fastapi import Request, HTTPException, status
from datetime import datetime, timezone

import logging

logging.basicConfig(
    filename = "app.log",
    filemode = "a",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    encoding='utf-8'
)

logger = logging.getLogger(__name__)

def get_event_or_404(db: Session, event_id: int):
    event = db.query(Event).filter(
    Event.id == event_id, 
    Event.is_delete == False
).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sự kiện không tồn tại"
        )
    return event

def get_staff_member(db: Session, event_id: int, user_id: int) -> Optional[EventStaff]:
    return db.query(EventStaff).filter(
        EventStaff.event_id == event_id,
        EventStaff.user_id == user_id
    ).first()

def check_is_owner(db: Session, event_id: int, user_id: int):
    staff = get_staff_member(db, event_id, user_id)
    if not staff or staff.role != "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ có OWNER mới có quyền thực hiện thao tác này"
        )

def check_is_member(db: Session, event_id: int, user_id: int):
    staff = get_staff_member(db, event_id, user_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải là thành viên của sự kiện này"
        )

def create_event_ser(event: EventCreate, current_user: User, db: Session) -> Event:
    new_event = Event(
        name=event.name.strip(),
        description=event.description,
        owner_id=current_user.id
    )
    db.add(new_event)

    try:
        db.flush()
        owner_staff = EventStaff(
            event_id=new_event.id,
            user_id=current_user.id,
            role="OWNER"
        )
        db.add(owner_staff)
        db.commit()
        db.refresh(new_event)
        logger.info(f"[CREATE EVENT] User ID={current_user.id} đã tạo Sự kiện ID={new_event.id} ('{new_event.name}')")
        return new_event
    except Exception as e:
        db.rollback()
        logger.error(f"[CREATE EVENT FAILED] User ID={current_user.id} thất bại khi tạo sự kiện | Lỗi: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload

def get_events_ser(
    current_user: User, 
    search: Optional[str], 
    db: Session,
    page: int = 1,
    limit: int = 10
) -> Dict[str, Any]:
    query = (
        db.query(Event)
        .options(joinedload(Event.event_staffs))
        .filter(
            Event.is_delete == False,
            Event.event_staffs.any(user_id=current_user.id)
        )
    )
    
    if search and search.strip():
        query = query.filter(Event.name.ilike(f"%{search.strip()}%"))
        
    total = query.count()
    skip = (page - 1) * limit
    events = query.offset(skip).limit(limit).all()
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "items": events
    }
def get_event_detail_ser(event_id: int, current_user: User, db: Session) -> Event:
    event = get_event_or_404(db, event_id)
    check_is_member(db, event_id, current_user.id)
    return event

def update_event_ser(event_id: int, event: EventUpdate, current_user: User, db: Session) -> Event:
    event_db = get_event_or_404(db, event_id)
    check_is_owner(db, event_id, current_user.id)

    if event.name is not None:
        event_db.name = event.name.strip()
    if event.description is not None:
        event_db.description = event.description

    try:
        db.commit()
        db.refresh(event_db)
        logger.info(f"[UPDATE EVENT] User ID={current_user.id} đã cập nhật Sự kiện ID={event_id}")
        return event_db
    except Exception as e:
        db.rollback()
        logger.error(f"[UPDATE EVENT FAILED] User ID={current_user.id} thất bại khi sửa Sự kiện ID={event_id} | Lỗi: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def delete_event_ser(event_id: int, current_user: User, db: Session):
    event = get_event_or_404(db, event_id)
    check_is_owner(db, event_id, current_user.id)
    try:
        event.is_delete = True
        event.deleted_at = datetime.now(timezone.utc)
        
        db.commit()
        logger.info(f"[DELETE EVENT] User ID={current_user.id} đã xóa mềm Sự kiện ID={event_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"[DELETE EVENT FAILED] User ID={current_user.id} thất bại khi xóa Sự kiện ID={event_id} | Lỗi: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def add_member_ser(event_id: int, staff: EventStaffCreate, current_user: User, db: Session) -> EventStaff:
    get_event_or_404(db, event_id)
    check_is_owner(db, event_id, current_user.id)

    target_user = db.query(User).filter(User.id == staff.user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng được thêm không tồn tại")

    existing_staff = get_staff_member(db, event_id, staff.user_id)
    if existing_staff:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Thành viên đã có trong sự kiện")

    new_staff = EventStaff(
        event_id = event_id,
        user_id = staff.user_id,
        role = "MEMBER"
    )

    try:
        db.add(new_staff)
        db.commit()
        db.refresh(new_staff)
        logger.info(f"[ADD MEMBER] User ID={current_user.id} đã thêm User ID={staff.user_id} vào Sự kiện ID={event_id}")
        return new_staff
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


def remove_member_ser(event_id: int, user_id: int, current_user: User, db: Session) -> EventStaff:
    get_event_or_404(db, event_id)
    check_is_owner(db, event_id, current_user.id)

    target_staff = get_staff_member(db, event_id, user_id)
    if not target_staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thành viên không thuộc sự kiện này"
        )

    if target_staff.role == "OWNER":
        owner_count = db.query(EventStaff).filter(
            EventStaff.event_id == event_id,
            EventStaff.role == "OWNER"
        ).count()

        if owner_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể xóa OWNER cuối cùng khỏi sự kiện"
            )
    try:
        db.delete(target_staff)
        db.commit()
        logger.info(f"[REMOVE MEMBER] User ID={current_user.id} đã xóa User ID={user_id} khỏi Sự kiện ID={event_id}")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def get_members_ser(event_id: int, current_user: User, db:Session) ->List[EventStaff]:
    get_event_or_404(db, event_id)
    check_is_member(db, event_id, current_user.id)

    return db.query(EventStaff).filter(EventStaff.event_id == event_id).all()