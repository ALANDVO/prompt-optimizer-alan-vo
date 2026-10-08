from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, UserPrincipal
from app.core.audit import record_audit
from app.models.db_models import OptimizationRecord
from app.models.schemas import (
    OptimizationRequest,
    OptimizationResponse,
    PaginatedResponse,
)
from app.services.optimizer import optimize_prompt

router = APIRouter(tags=["Optimization"])


@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_prompt_endpoint(
    req: OptimizationRequest,
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("operator")),
) -> OptimizationResponse:
    res = await optimize_prompt(
        prompt=req.prompt,
        target_domain=req.target_domain,
        strategy=req.strategy,
        use_advisory_llm=req.use_advisory_llm,
    )

    record = OptimizationRecord(
        original_prompt=res["original_prompt"],
        optimized_prompt=res["optimized_prompt"],
        strategy=res["strategy"],
        target_domain=res["target_domain"],
        score_before=res["score_before"],
        score_after=res["score_after"],
        improvement_delta=res["improvement_delta"],
        diff_summary=res["diff_summary"],
        advisory_notes=res["advisory_notes"],
        llm_used=res["llm_used"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    record_audit(
        db,
        user_id=current_user.user_id,
        username=current_user.username,
        action="optimize_prompt",
        resource="optimization_record",
        resource_id=str(record.id),
        details={
            "strategy": res["strategy"],
            "delta": res["improvement_delta"],
            "llm_used": res["llm_used"],
        },
    )

    return OptimizationResponse(
        id=record.id,
        original_prompt=record.original_prompt,
        optimized_prompt=record.optimized_prompt,
        strategy=record.strategy,
        target_domain=record.target_domain,
        score_before=record.score_before,
        score_after=record.score_after,
        improvement_delta=record.improvement_delta,
        diff_summary=record.diff_summary,
        advisory_notes=record.advisory_notes,
        llm_used=record.llm_used,
        created_at=record.created_at,
    )


@router.get("/optimizations", response_model=PaginatedResponse[OptimizationResponse])
@router.get("/optimize", response_model=PaginatedResponse[OptimizationResponse])
def list_optimizations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("viewer")),
) -> PaginatedResponse[OptimizationResponse]:
    query = db.query(OptimizationRecord)
    total = query.count()
    records = query.order_by(OptimizationRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [
        OptimizationResponse(
            id=r.id,
            original_prompt=r.original_prompt,
            optimized_prompt=r.optimized_prompt,
            strategy=r.strategy,
            target_domain=r.target_domain,
            score_before=r.score_before,
            score_after=r.score_after,
            improvement_delta=r.improvement_delta,
            diff_summary=r.diff_summary,
            advisory_notes=r.advisory_notes,
            llm_used=r.llm_used,
            created_at=r.created_at,
        )
        for r in records
    ]

    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/optimizations/{opt_id}", response_model=OptimizationResponse)
@router.get("/optimize/{opt_id}", response_model=OptimizationResponse)
def get_optimization(
    opt_id: int,
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("viewer")),
) -> OptimizationResponse:
    r = db.query(OptimizationRecord).filter(OptimizationRecord.id == opt_id).first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Optimization record not found.")

    return OptimizationResponse(
        id=r.id,
        original_prompt=r.original_prompt,
        optimized_prompt=r.optimized_prompt,
        strategy=r.strategy,
        target_domain=r.target_domain,
        score_before=r.score_before,
        score_after=r.score_after,
        improvement_delta=r.improvement_delta,
        diff_summary=r.diff_summary,
        advisory_notes=r.advisory_notes,
        llm_used=r.llm_used,
        created_at=r.created_at,
    )
