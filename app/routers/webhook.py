from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import Tenant
from app.services.conversation_service import add_message, get_or_create_contact, get_or_create_conversation
from app.services.sse_service import sse_broker

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.get("/whatsapp")
def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.verify_token:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Token de verificação inválido")


@router.post("/whatsapp")
def receive_whatsapp_event(payload: dict, db: Session = Depends(get_db)):
    entries = payload.get("entry", [])
    saved_count = 0

    for entry in entries:
        for change in entry.get("changes", []):
            value = change.get("value", {})
            contacts = value.get("contacts", [])
            messages = value.get("messages", [])
            metadata = value.get("metadata", {})
            phone_number_id = metadata.get("phone_number_id")

            tenant = db.scalar(select(Tenant).where(Tenant.phone_number_id == phone_number_id))
            if not tenant:
                continue

            for message in messages:
                wa_id = message.get("from")
                message_id = message.get("id")
                msg_type = message.get("type", "text")
                text_body = (message.get("text") or {}).get("body") or f"[{msg_type}]"
                if not wa_id:
                    continue

                contact_name = None
                if contacts:
                    contact_name = contacts[0].get("profile", {}).get("name")

                contact = get_or_create_contact(db, tenant_id=tenant.id, wa_id=wa_id, name=contact_name)
                conversation = get_or_create_conversation(db, tenant_id=tenant.id, contact_id=contact.id)
                saved = add_message(
                    db,
                    tenant_id=tenant.id,
                    conversation_id=conversation.id,
                    direction="incoming",
                    body=text_body,
                    sender_wa_id=wa_id,
                    provider_message_id=message_id,
                    content_type=msg_type,
                )
                db.commit()
                saved_count += 1

                sse_broker.publish(
                    tenant.id,
                    {
                        "conversation_id": conversation.id,
                        "message": {
                            "id": saved.id,
                            "direction": saved.direction,
                            "body": saved.body,
                            "created_at": saved.created_at.isoformat() if saved.created_at else None,
                        },
                    },
                )

    return {"status": "ok", "saved": saved_count}
