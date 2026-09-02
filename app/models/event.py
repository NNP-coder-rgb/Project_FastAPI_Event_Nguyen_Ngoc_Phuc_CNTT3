from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    is_delete = Column(Boolean, default=False)
    delete_at = Column(DateTime, default=datetime.now)

    owner = relationship("User", back_populates="events")
    event_tasks = relationship("EventTask", back_populates="event", cascade="all, delete-orphan")
    event_staffs = relationship("EventStaff", back_populates="event", cascade="all, delete-orphan")

class EventStaff(Base):
    __tablename__ = "event_staff"
    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    role = Column(String(20), nullable=False)
    joined_at = Column(DateTime, default=datetime.now, nullable=False)

    user = relationship("User", back_populates="event_staffs")
    event = relationship("Event", back_populates="event_staffs")
