from fastapi import Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Tenant


def resolve_tenant_id(x_tenant_id: int | None = Header(default=None)) -> int:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Header X-Tenant-Id é obrigatório")
    return x_tenant_id


def get_tenant_or_404(db: Session, tenant_id: int) -> Tenant:
    tenant = db.scalar(select(Tenant).where(Tenant.id == tenant_id))
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant
