# WhatsApp SaaS - Backend (FastAPI)

Backend multi-tenant para atendimento e disparo via WhatsApp Cloud API (Meta), com atualização em tempo real usando SSE.

## Stack
- FastAPI
- PostgreSQL + SQLAlchemy
- SSE (Server-Sent Events)

## Estrutura
- `app/main.py`
- `app/routers/`
- `app/services/`
- `app/models/`

## Executar localmente
1. Configure `.env` com `DATABASE_URL` (PostgreSQL), `VERIFY_TOKEN`, etc.
2. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Rode a API:
   ```bash
   uvicorn app.main:app --reload
   ```

## Multi-tenant
Todos os endpoints protegidos por tenant usam o header `X-Tenant-Id`.

## Endpoints principais
- `POST /api/webhook/whatsapp`
- `GET /api/webhook/whatsapp` (verificação Meta)
- `POST /api/messages/send`
- `POST /api/messages/send/batch`
- `GET /api/conversations`
- `GET /api/conversations/{id}/messages`
- `GET /api/sse/conversations`
- `GET /api/settings/meta`
- `PUT /api/settings/meta`
