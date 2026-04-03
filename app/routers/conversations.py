from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models import Conversation, Message
from app.schemas import ConversationOut, MessageOut
from app.services.tenant_service import resolve_tenant_id

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationOut])
def list_conversations(tenant_id: int = Depends(resolve_tenant_id), db: Session = Depends(get_db)):
    conversations = db.scalars(
        select(Conversation)
        .options(joinedload(Conversation.contact), joinedload(Conversation.messages))
        .where(Conversation.tenant_id == tenant_id)
        .order_by(desc(Conversation.last_message_at))
    ).unique().all()

    output: list[ConversationOut] = []
    for conversation in conversations:
        preview = conversation.messages[-1].body if conversation.messages else None
        output.append(
            ConversationOut(
                id=conversation.id,
                status=conversation.status,
                last_message_at=conversation.last_message_at,
                contact={
                    "id": conversation.contact.id,
                    "wa_id": conversation.contact.wa_id,
                    "name": conversation.contact.name,
                },
                last_message_preview=preview,
            )
        )
    return output


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def list_messages(conversation_id: int, tenant_id: int = Depends(resolve_tenant_id), db: Session = Depends(get_db)):
    conversation = db.scalar(
        select(Conversation).where(Conversation.id == conversation_id, Conversation.tenant_id == tenant_id)
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")

    messages = db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation_id, Message.tenant_id == tenant_id)
        .order_by(Message.created_at.asc())
    ).all()

    return [
        MessageOut(
            id=m.id,
            conversation_id=m.conversation_id,
            direction=m.direction,
            content_type=m.content_type,
            body=m.body,
            sender_wa_id=m.sender_wa_id,
            provider_message_id=m.provider_message_id,
            created_at=m.created_at,
        )
        for m in messages
    ]
