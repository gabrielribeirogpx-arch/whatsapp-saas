from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import TenantConfigOut, TenantConfigUpsert
from app.services.tenant_service import get_tenant_or_404, resolve_tenant_id

router = APIRouter(prefix="/settings", tags=["settings"])


def _mask_secret(secret: str | None) -> str | None:
    if not secret:
        return None
    if len(secret) <= 8:
        return "*" * len(secret)
    return f"{secret[:4]}...{secret[-4:]}"


@router.get("/meta", response_model=TenantConfigOut)
def get_meta_settings(tenant_id: int = Depends(resolve_tenant_id), db: Session = Depends(get_db)):
    tenant = get_tenant_or_404(db, tenant_id)
    return TenantConfigOut(
        id=tenant.id,
        name=tenant.name,
        meta_token_masked=_mask_secret(tenant.meta_token),
        phone_number_id=tenant.phone_number_id,
    )


@router.put("/meta", response_model=TenantConfigOut)
def upsert_meta_settings(
    payload: TenantConfigUpsert, tenant_id: int = Depends(resolve_tenant_id), db: Session = Depends(get_db)
):
    tenant = get_tenant_or_404(db, tenant_id)
    tenant.name = payload.name
    tenant.meta_token = payload.meta_token
    tenant.phone_number_id = payload.phone_number_id
    db.add(tenant)
    db.commit()

    return TenantConfigOut(
        id=tenant.id,
        name=tenant.name,
        meta_token_masked=_mask_secret(tenant.meta_token),
        phone_number_id=tenant.phone_number_id,
    )
