from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, UserPrincipal
from app.core.audit import record_audit
from app.models.db_models import PromptTemplate
from app.models.schemas import (
    PromptCreateRequest,
    PromptUpdateRequest,
    PromptResponse,
    PaginatedResponse,
)

router = APIRouter(prefix="/prompts", tags=["Prompt Library"])


@router.post("", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
def create_prompt_template(
    req: PromptCreateRequest,
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("operator")),
) -> PromptResponse:
    existing = db.query(PromptTemplate).filter(PromptTemplate.name == req.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Prompt template with name '{req.name}' already exists.",
        )

    item = PromptTemplate(
        name=req.name,
        prompt=req.prompt,
        domain=req.domain,
        tags=req.tags,
        version=1,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    record_audit(
        db,
        user_id=current_user.user_id,
        username=current_user.username,
        action="create_prompt_template",
        resource="prompt_template",
        resource_id=str(item.id),
        details={"name": item.name, "domain": item.domain},
    )

    return PromptResponse(
        id=item.id,
        name=item.name,
        prompt=item.prompt,
        domain=item.domain,
        tags=item.tags,
        version=item.version,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("", response_model=PaginatedResponse[PromptResponse])
def list_prompt_templates(
    domain: str | None = None,
    tag: str | None = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("viewer")),
) -> PaginatedResponse[PromptResponse]:
    query = db.query(PromptTemplate)
    if domain:
        query = query.filter(PromptTemplate.domain == domain)
    if tag:
        query = query.filter(PromptTemplate.tags.contains(tag))
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (PromptTemplate.name.like(pattern)) | (PromptTemplate.prompt.like(pattern))
        )

    total = query.count()
    items = query.order_by(PromptTemplate.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        items=[
            PromptResponse(
                id=i.id,
                name=i.name,
                prompt=i.prompt,
                domain=i.domain,
                tags=i.tags,
                version=i.version,
                created_at=i.created_at,
                updated_at=i.updated_at,
            )
            for i in items
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{prompt_id}", response_model=PromptResponse)
def get_prompt_template(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("viewer")),
) -> PromptResponse:
    item = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt template not found.",
        )
    return PromptResponse(
        id=item.id,
        name=item.name,
        prompt=item.prompt,
        domain=item.domain,
        tags=item.tags,
        version=item.version,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.put("/{prompt_id}", response_model=PromptResponse)
def update_prompt_template(
    prompt_id: int,
    req: PromptUpdateRequest,
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("operator")),
) -> PromptResponse:
    item = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt template not found.",
        )

    if req.prompt is not None:
        item.prompt = req.prompt
    if req.domain is not None:
        item.domain = req.domain
    if req.tags is not None:
        item.tags = req.tags

    item.version += 1
    db.commit()
    db.refresh(item)

    record_audit(
        db,
        user_id=current_user.user_id,
        username=current_user.username,
        action="update_prompt_template",
        resource="prompt_template",
        resource_id=str(item.id),
        details={"version": item.version},
    )

    return PromptResponse(
        id=item.id,
        name=item.name,
        prompt=item.prompt,
        domain=item.domain,
        tags=item.tags,
        version=item.version,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.delete("/{prompt_id}")
def delete_prompt_template(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("admin")),
) -> dict[str, str]:
    item = db.query(PromptTemplate).filter(PromptTemplate.id == prompt_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt template not found.",
        )

    db.delete(item)
    db.commit()

    record_audit(
        db,
        user_id=current_user.user_id,
        username=current_user.username,
        action="delete_prompt_template",
        resource="prompt_template",
        resource_id=str(prompt_id),
        details={"name": item.name},
    )

    return {"status": "deleted", "id": str(prompt_id)}
