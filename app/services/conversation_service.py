from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Contact, Conversation, Message


def get_or_create_contact(db: Session, *, tenant_id: int, wa_id: str, name: str | None = None) -> Contact:
    contact = db.scalar(select(Contact).where(Contact.tenant_id == tenant_id, Contact.wa_id == wa_id))
    if contact:
        if name and contact.name != name:
            contact.name = name
            db.add(contact)
        return contact

    contact = Contact(tenant_id=tenant_id, wa_id=wa_id, name=name)
    db.add(contact)
    db.flush()
    return contact


def get_or_create_conversation(db: Session, *, tenant_id: int, contact_id: int) -> Conversation:
    conversation = db.scalar(
        select(Conversation).where(Conversation.tenant_id == tenant_id, Conversation.contact_id == contact_id)
    )
    if conversation:
        return conversation

    conversation = Conversation(tenant_id=tenant_id, contact_id=contact_id)
    db.add(conversation)
    db.flush()
    return conversation


def add_message(
    db: Session,
    *,
    tenant_id: int,
    conversation_id: int,
    direction: str,
    body: str,
    sender_wa_id: str | None,
    provider_message_id: str | None,
    content_type: str = "text",
) -> Message:
    message = Message(
        tenant_id=tenant_id,
        conversation_id=conversation_id,
        direction=direction,
        body=body,
        sender_wa_id=sender_wa_id,
        provider_message_id=provider_message_id,
        content_type=content_type,
    )
    db.add(message)
    conversation = db.get(Conversation, conversation_id)
    if conversation:
        conversation.last_message_at = datetime.now(timezone.utc)
        db.add(conversation)
    db.flush()
    return message
