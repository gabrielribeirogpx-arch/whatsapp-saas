from __future__ import annotations

from typing import Any

import requests
from fastapi import HTTPException

from app.config import settings
from app.models import Tenant


def graph_url(phone_number_id: str) -> str:
    return f"https://graph.facebook.com/{settings.meta_graph_version}/{phone_number_id}/messages"


def send_text_message(*, tenant: Tenant, to: str, body: str) -> dict[str, Any]:
    if not tenant.meta_token or not tenant.phone_number_id:
        raise HTTPException(status_code=400, detail="Tenant sem configuração da Meta")

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": body},
    }
    response = requests.post(
        graph_url(tenant.phone_number_id),
        headers={"Authorization": f"Bearer {tenant.meta_token}", "Content-Type": "application/json"},
        json=payload,
        timeout=15,
    )
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Erro Meta API: {response.text}")
    return response.json()


def build_template_payload(*, to: str, template_name: str) -> dict[str, Any]:
    return {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {"name": template_name, "language": {"code": "pt_BR"}},
    }
