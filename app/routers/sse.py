from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.services.sse_service import sse_broker
from app.services.tenant_service import resolve_tenant_id

router = APIRouter(prefix="/sse", tags=["sse"])


@router.get("/conversations")
async def stream_conversations(tenant_id: int = Depends(resolve_tenant_id)):
    async def event_generator():
        yield "event: ready\ndata: connected\n\n"
        async for event in sse_broker.subscribe(tenant_id):
            yield event

    return StreamingResponse(event_generator(), media_type="text/event-stream")
