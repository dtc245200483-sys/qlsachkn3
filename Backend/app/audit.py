from sqlalchemy.orm import Session

from .models import AuditLog, User


def write_audit_log(
    db: Session,
    user: User | None,
    action: str,
    entity: str,
    entity_id: str | None = None,
    details: str | None = None,
) -> None:
    db.add(
        AuditLog(
            username=user.username if user is not None else None,
            role=user.role if user is not None else None,
            action=action,
            entity=entity,
            entity_id=entity_id,
            details=details,
        )
    )
