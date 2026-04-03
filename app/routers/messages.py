from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Contact, Conversation
from app.schemas import BatchSendRequest, SendMessageRequest, SendMessageResponse
from app.services.conversation_service import add_message, get_or_create_contact, get_or_create_conversation
from app.services.sse_service import sse_broker
from app.services.tenant_service import get_tenant_or_404, resolve_tenant_id
from app.services.whatsapp_service import build_template_payload, send_text_message

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/send", response_model=SendMessageResponse)
def send_message(payload: SendMessageRequest, tenant_id: int = Depends(resolve_tenant_id), db: Session = Depends(get_db)):
    tenant = get_tenant_or_404(db, tenant_id)

    conversation = None
    to = payload.to
    if payload.conversation_id:
        conversation = db.scalar(
            select(Conversation).where(Conversation.id == payload.conversation_id, Conversation.tenant_id == tenant_id)
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversa não encontrada")
        to = conversation.contact.wa_id

    if not to:
        raise HTTPException(status_code=400, detail="Informe 'to' ou conversation_id")

    if payload.type == "template":
        if not payload.template_name:
            raise HTTPException(status_code=400, detail="template_name é obrigatório")
        provider_response = {"template_payload": build_template_payload(to=to, template_name=payload.template_name)}
        provider_id = None
        body = f"[template:{payload.template_name}]"
        content_type = "template"
    else:
        provider_response = send_text_message(tenant=tenant, to=to, body=payload.body)
        provider_messages = provider_response.get("messages", [])
        provider_id = provider_messages[0].get("id") if provider_messages else None
        body = payload.body
        content_type = "text"

    if conversation is None:
        contact = get_or_create_contact(db, tenant_id=tenant_id, wa_id=to)
        conversation = get_or_create_conversation(db, tenant_id=tenant_id, contact_id=contact.id)

    message = add_message(
        db,
        tenant_id=tenant_id,
        conversation_id=conversation.id,
        direction="outgoing",
        body=body,
        sender_wa_id=tenant.phone_number_id,
        provider_message_id=provider_id,
        content_type=content_type,
    )
    db.commit()

    sse_broker.publish(
        tenant_id,
        {
            "conversation_id": conversation.id,
            "message": {
                "id": message.id,
                "direction": message.direction,
                "body": message.body,
                "created_at": message.created_at.isoformat() if message.created_at else None,
            },
        },
    )

    return SendMessageResponse(message_id=message.id, provider_message_id=provider_id)


@router.post("/send/batch")
def send_batch(payload: BatchSendRequest, tenant_id: int = Depends(resolve_tenant_id), db: Session = Depends(get_db)):
    sent = []
    for item in payload.recipients:
        result = send_message(
            SendMessageRequest(to=item.to, body=payload.body), tenant_id=tenant_id, db=db
        )
        sent.append(result.model_dump())
    return {"status": "ok", "sent": sent}
