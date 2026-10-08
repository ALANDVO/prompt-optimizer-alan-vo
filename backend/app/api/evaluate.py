import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, UserPrincipal
from app.core.audit import record_audit
from app.models.db_models import EvaluationRecord
from app.models.schemas import (
    EvaluationRequest,
    EvaluationResponse,
    PaginatedResponse,
    DimensionScore,
)
from app.services.evaluator import evaluate_prompt_quality

router = APIRouter(tags=["Evaluation"])


def to_eval_response(r: EvaluationRecord, dims: list[DimensionScore] | None = None) -> EvaluationResponse:
    w = json.loads(r.weak_areas) if r.weak_areas else []
    rc = json.loads(r.recommendations) if r.recommendations else []
    return EvaluationResponse(
        id=r.id, prompt=r.prompt, overall_score=r.overall_score, grade=r.grade,
        clarity_score=r.clarity_score, specificity_score=r.specificity_score,
        structure_score=r.structure_score, constraints_score=r.constraints_score,
        output_spec_score=r.output_spec_score, role_score=r.role_score,
        examples_score=r.examples_score, safety_score=r.safety_score,
        dimensions=dims or [], weak_areas=w, recommendations=rc, created_at=r.created_at,
    )


@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate_prompt(
    req: EvaluationRequest,
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("viewer")),
) -> EvaluationResponse:
    res = evaluate_prompt_quality(req.prompt, req.domain)

    record = EvaluationRecord(
        prompt=req.prompt,
        overall_score=res["overall_score"],
        grade=res["grade"],
        clarity_score=res["clarity_score"],
        specificity_score=res["specificity_score"],
        structure_score=res["structure_score"],
        constraints_score=res["constraints_score"],
        output_spec_score=res["output_spec_score"],
        role_score=res["role_score"],
        examples_score=res["examples_score"],
        safety_score=res["safety_score"],
        weak_areas=json.dumps(res["weak_areas"]),
        recommendations=json.dumps(res["recommendations"]),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    record_audit(
        db,
        user_id=current_user.user_id,
        username=current_user.username,
        action="evaluate_prompt",
        resource="evaluation_record",
        resource_id=str(record.id),
        details={"score": res["overall_score"], "grade": res["grade"]},
    )

    return to_eval_response(record, res["dimensions"])


@router.get("/evaluations", response_model=PaginatedResponse[EvaluationResponse])
@router.get("/evaluate", response_model=PaginatedResponse[EvaluationResponse])
def list_evaluations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("viewer")),
) -> PaginatedResponse[EvaluationResponse]:
    query = db.query(EvaluationRecord)
    total = query.count()
    records = query.order_by(EvaluationRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = [to_eval_response(r) for r in records]
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/evaluations/{eval_id}", response_model=EvaluationResponse)
@router.get("/evaluate/{eval_id}", response_model=EvaluationResponse)
def get_evaluation(
    eval_id: int,
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("viewer")),
) -> EvaluationResponse:
    r = db.query(EvaluationRecord).filter(EvaluationRecord.id == eval_id).first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation record not found.")

    res = evaluate_prompt_quality(r.prompt)
    return to_eval_response(r, res["dimensions"])
