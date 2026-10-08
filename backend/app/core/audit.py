import json
from typing import Any
from sqlalchemy.orm import Session
from app.models.db_models import AuditLog


def record_audit(
    db: Session,
    user_id: str,
    username: str,
    action: str,
    resource: str,
    resource_id: str = "",
    details: dict[str, Any] | str | None = None,
) -> AuditLog:
    if isinstance(details, dict):
        # Redact any key that looks like an authorization or secret
        cleaned = {
            k: ("[REDACTED]" if "key" in k.lower() or "secret" in k.lower() or "token" in k.lower() else v)
            for k, v in details.items()
        }
        details_str = json.dumps(cleaned)
    elif details is None:
        details_str = ""
    else:
        details_str = str(details)

    log_entry = AuditLog(
        user_id=user_id,
        username=username,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details_str,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
