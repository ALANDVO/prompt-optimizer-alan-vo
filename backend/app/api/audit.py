from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, UserPrincipal
from app.models.db_models import AuditLog
from app.models.schemas import AuditLogResponse, PaginatedResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=PaginatedResponse[AuditLogResponse])
def list_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("admin")),
) -> PaginatedResponse[AuditLogResponse]:
    query = db.query(AuditLog)
    total = query.count()
    records = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [
        AuditLogResponse(
            id=r.id,
            user_id=r.user_id,
            username=r.username,
            action=r.action,
            resource=r.resource,
            resource_id=r.resource_id,
            details=r.details,
            created_at=r.created_at,
        )
        for r in records
    ]

    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)
