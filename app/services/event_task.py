from typing import Any, Optional, Dict
from fastapi import HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from app.models.event import EventStaff
from app.models.event_task import EventTask
from app.models.user import User
from app.schemas.event_task import EventTaskCreate, EventTaskUpdate


VALID_STATUSES = ["TODO", "IN_PROGRESS", "DONE"]
VALID_PRIORITIES = ["LOW", "MEDIUM", "HIGH"]

def validate_status_and_priority(status_val: Optional[str] = None, priority_val: Optional[str] = None):
    if status_val is not None and status_val not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status không hợp lệ. Phải là một trong: {', '.join(VALID_STATUSES)}"
        )

    if priority_val is not None and priority_val not in VALID_PRIORITIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Priority không hợp lệ. Phải là một trong: {', '.join(VALID_PRIORITIES)}"
        )


def check_user_in_event(db: Session, event_id: int, user_id: int) -> EventStaff:
    staff = db.query(EventStaff).filter(
        EventStaff.event_id == event_id,
        EventStaff.user_id == user_id
    ).first()

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập công việc của sự kiện này"
        )
    return staff

def check_assignee_in_event(db: Session, event_id: int, assignee_id: int):
    staff = db.query(EventStaff).filter(
        EventStaff.event_id == event_id,
        EventStaff.user_id == assignee_id
    ).first()

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Người được giao việc (assignee) phải là nhân sự thuộc sự kiện này"
        )

def get_task_or_404(db: Session, task_id: int) -> EventTask:
    task = db.query(EventTask).filter(EventTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Công việc không tồn tại"
        )
    return task

def create_task_ser(event_id: int, task: EventTaskCreate, current_user: User, db: Session) -> EventTask:
    check_user_in_event(db, event_id, current_user.id)

    validate_status_and_priority(task.status, task.priority)

    if task.assignee_id:
        check_assignee_in_event(db, event_id, task.assignee_id)

    new_task = EventTask(
        event_id = event_id,
        title = task.title.strip(),
        description = task.description,
        status = task.status,
        priority = task.priority,
        due_date = task.due_date,
        assignee_id = task.assignee_id
    )

    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


def get_event_tasks_ser(
        event_id: int, current_user: User, db: Session, status_filter: Optional[str] = None,
        priority_filter: Optional[str] = None, assignee_id: Optional[int] = None, search: Optional[str] = None,
        page: int = 1, size: int = 10, sort_by: str = "created_at", order: str = "desc"
) -> Dict[str, Any]:
    check_user_in_event(db, event_id, current_user.id)
    query = db.query(EventTask).filter(EventTask.event_id == event_id)

    if status_filter:
        query = query.filter(EventTask.status == status_filter)
    if priority_filter:
        query = query.filter(EventTask.priority == priority_filter)
    if assignee_id:
        query = query.filter(EventTask.assignee_id == assignee_id)
    if search:
        query = query.filter(EventTask.title.ilike(f"%{search.strip()}%"))

    total_items = query.count()

    if sort_by not in ["created_at", "due_date"]:
        sort_by = "created_at"
    sort_column = getattr(EventTask, sort_by)
    query = query.order_by(desc(sort_column) if order.lower() == "desc" else asc(sort_column))

    offset = (page-1)*size
    tasks = query.offset(offset).limit(size).all()

    return {
        "items": tasks,
        "total": total_items,
        "page": page,
        "size": size,
        "total_page": (total_items + size - 1) // size if size > 0 else 1
    }

def get_task_detail_ser(task_id: int, current_user: User, db: Session) -> EventTask:
    task = get_task_or_404(db, task_id)
    check_user_in_event(db, task.event_id, current_user.id)
    return task

def update_task_ser(task_id: int, task: EventTaskUpdate, current_user: User, db: Session) -> EventTask:
    task_db = get_task_or_404(db, task_id)
    staff = check_user_in_event(db, task_db.event_id, current_user.id)

    update_data = task.model_dump(exclude_unset=True)

    if staff.role != "OWNER":
        if task_db.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền sửa công việc này"
            )

    validate_status_and_priority(task.status, task.priority)

    if task.assignee_id is not None:
        check_assignee_in_event(db, task_db.event_id, task.assignee_id)

    for field, value in update_data.items():
        setattr(task_db, field, value)
    try:
        db.commit()
        db.refresh(task_db)
        return task_db
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def delete_task_ser(task_id: int, current_user: User, db: Session):
    task = get_task_or_404(db, task_id)
    staff = check_user_in_event(db, task.event_id, current_user.id)

    if staff.role != "OWNER" and task.assignee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ có OWNER hoặc người được phân công mới có thể xóa công việc"
        )
    try:
        db.delete(task)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )