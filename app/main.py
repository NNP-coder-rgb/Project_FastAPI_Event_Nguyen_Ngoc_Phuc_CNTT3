from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from app.db.database import Base, engine
from app.core.exception import (
    http_exception_handler,
    global_exception_handler,
    validation_exception_handler
)

from app.routers.health import router as router_health_check
from app.models.user import User
from app.models.event import Event, EventStaff
from app.models.event_task import EventTask
from app.routers.auth import router as router_auth
from app.routers.user import router as router_user
from app.routers.event import router as router_event
from app.routers.event_task import router as router_event_task

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.routers.auth import limiter

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Management API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(router_health_check)
app.include_router(router_auth)
app.include_router(router_user)
app.include_router(router_event)
app.include_router(router_event_task)