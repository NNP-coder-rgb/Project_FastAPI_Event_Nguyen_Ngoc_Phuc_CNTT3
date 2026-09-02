from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class EventTask(Base):
    __tablename__ = "event_tasks"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    assignee_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), nullable=False)
    priority = Column(String(20), nullable=False)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    event = relationship("Event", back_populates="event_tasks")
    assignee = relationship("User", back_populates="event_tasks")