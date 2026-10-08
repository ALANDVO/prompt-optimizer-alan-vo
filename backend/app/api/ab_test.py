import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, UserPrincipal
from app.core.audit import record_audit
from app.models.db_models import ABTestRecord
from app.models.schemas import (
    ABTestRequest,
    ABTestResponse,
    PaginatedResponse,
    ABCaseResult,
)
from app.services.ab_test import run_ab_test_suite

router = APIRouter(tags=["A/B Testing"])


@router.post("/ab-test", response_model=ABTestResponse)
def run_ab_test_endpoint(
    req: ABTestRequest,
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("operator")),
) -> ABTestResponse:
    res = run_ab_test_suite(req.prompt_a, req.prompt_b, req.cases)

    details_json = json.dumps([d.model_dump() for d in res["details"]])
    record = ABTestRecord(
        prompt_a=req.prompt_a,
        prompt_b=req.prompt_b,
        cases_count=res["cases_count"],
        wins_a=res["wins_a"],
        wins_b=res["wins_b"],
        ties=res["ties"],
        winner=res["winner"],
        details=details_json,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    record_audit(
        db,
        user_id=current_user.user_id,
        username=current_user.username,
        action="run_ab_test",
        resource="ab_test_record",
        resource_id=str(record.id),
        details={"winner": res["winner"], "cases": res["cases_count"]},
    )

    return ABTestResponse(
        id=record.id,
        prompt_a=record.prompt_a,
        prompt_b=record.prompt_b,
        cases_count=record.cases_count,
        wins_a=record.wins_a,
        wins_b=record.wins_b,
        ties=record.ties,
        winner=record.winner,
        confidence=res["confidence"],
        details=res["details"],
        created_at=record.created_at,
    )


@router.get("/ab-tests", response_model=PaginatedResponse[ABTestResponse])
@router.get("/ab-test", response_model=PaginatedResponse[ABTestResponse])
def list_ab_tests(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("viewer")),
) -> PaginatedResponse[ABTestResponse]:
    query = db.query(ABTestRecord)
    total = query.count()
    records = query.order_by(ABTestRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items: list[ABTestResponse] = []
    for r in records:
        raw_details = json.loads(r.details) if r.details else []
        details = [ABCaseResult(**d) for d in raw_details]
        conf = round(max(r.wins_a, r.wins_b) / r.cases_count, 2) if r.cases_count else 0.5
        items.append(
            ABTestResponse(
                id=r.id,
                prompt_a=r.prompt_a,
                prompt_b=r.prompt_b,
                cases_count=r.cases_count,
                wins_a=r.wins_a,
                wins_b=r.wins_b,
                ties=r.ties,
                winner=r.winner,
                confidence=conf,
                details=details,
                created_at=r.created_at,
            )
        )

    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/ab-tests/{test_id}", response_model=ABTestResponse)
@router.get("/ab-test/{test_id}", response_model=ABTestResponse)
def get_ab_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("viewer")),
) -> ABTestResponse:
    r = db.query(ABTestRecord).filter(ABTestRecord.id == test_id).first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="A/B test record not found.")

    raw_details = json.loads(r.details) if r.details else []
    details = [ABCaseResult(**d) for d in raw_details]
    conf = round(max(r.wins_a, r.wins_b) / r.cases_count, 2) if r.cases_count else 0.5

    return ABTestResponse(
        id=r.id,
        prompt_a=r.prompt_a,
        prompt_b=r.prompt_b,
        cases_count=r.cases_count,
        wins_a=r.wins_a,
        wins_b=r.wins_b,
        ties=r.ties,
        winner=r.winner,
        confidence=conf,
        details=details,
        created_at=r.created_at,
    )
