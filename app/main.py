from fastapi import FastAPI
from sqlalchemy import select

from app.config import settings
from app.db import Base, SessionLocal, engine
from app.models import Tenant
from app.routers import conversations, messages, settings as settings_router, sse, webhook

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        existing = db.scalar(select(Tenant.id).limit(1))
        if not existing:
            db.add(Tenant(name="Tenant Demo"))
            db.commit()


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(webhook.router, prefix=settings.api_prefix)
app.include_router(messages.router, prefix=settings.api_prefix)
app.include_router(conversations.router, prefix=settings.api_prefix)
app.include_router(sse.router, prefix=settings.api_prefix)
app.include_router(settings_router.router, prefix=settings.api_prefix)
