from datetime import datetime

from pydantic import BaseModel, Field


class ContactOut(BaseModel):
    id: int
    wa_id: str
    name: str | None = None


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    direction: str
    content_type: str
    body: str
    sender_wa_id: str | None = None
    provider_message_id: str | None = None
    created_at: datetime


class ConversationOut(BaseModel):
    id: int
    status: str
    last_message_at: datetime
    contact: ContactOut
    last_message_preview: str | None = None


class SendMessageRequest(BaseModel):
    to: str | None = Field(default=None, description="Telefone com DDI")
    conversation_id: int | None = None
    body: str = Field(min_length=1)
    type: str = Field(default="text", pattern="^(text|template)$")
    template_name: str | None = None


class SendMessageResponse(BaseModel):
    message_id: int
    provider_message_id: str | None = None


class BatchItem(BaseModel):
    to: str


class BatchSendRequest(BaseModel):
    recipients: list[BatchItem]
    body: str = Field(min_length=1)


class TenantConfigUpsert(BaseModel):
    name: str = Field(min_length=2)
    meta_token: str
    phone_number_id: str


class TenantConfigOut(BaseModel):
    id: int
    name: str
    meta_token_masked: str | None
    phone_number_id: str | None
