import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, UserPrincipal
from app.core.audit import record_audit
from app.models.db_models import BenchmarkRecord
from app.models.schemas import (
    BenchmarkRequest,
    BenchmarkResponse,
    BenchmarkModelResult,
    PaginatedResponse,
)
from app.services.benchmark import run_model_benchmarking

router = APIRouter(tags=["Benchmarking"])


@router.post("/benchmark", response_model=BenchmarkResponse)
def run_benchmark_endpoint(
    req: BenchmarkRequest,
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("operator")),
) -> BenchmarkResponse:
    res = run_model_benchmarking(req.prompt, req.models)

    results_json = json.dumps([r.model_dump() for r in res["results"]])
    record = BenchmarkRecord(
        prompt=req.prompt,
        models=json.dumps(req.models),
        results=results_json,
        best_model=res["best_model"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    record_audit(
        db,
        user_id=current_user.user_id,
        username=current_user.username,
        action="run_benchmark",
        resource="benchmark_record",
        resource_id=str(record.id),
        details={"best_model": res["best_model"], "models_count": len(req.models)},
    )

    return BenchmarkResponse(
        id=record.id,
        prompt=record.prompt,
        results=res["results"],
        best_model=record.best_model,
        benchmarked_at=record.created_at,
    )


@router.get("/benchmarks", response_model=PaginatedResponse[BenchmarkResponse])
@router.get("/benchmark", response_model=PaginatedResponse[BenchmarkResponse])
def list_benchmarks(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("viewer")),
) -> PaginatedResponse[BenchmarkResponse]:
    query = db.query(BenchmarkRecord)
    total = query.count()
    records = query.order_by(BenchmarkRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items: list[BenchmarkResponse] = []
    for r in records:
        raw_res = json.loads(r.results) if r.results else []
        model_results = [BenchmarkModelResult(**m) for m in raw_res]
        items.append(
            BenchmarkResponse(
                id=r.id,
                prompt=r.prompt,
                results=model_results,
                best_model=r.best_model,
                benchmarked_at=r.created_at,
            )
        )

    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/benchmarks/{bm_id}", response_model=BenchmarkResponse)
@router.get("/benchmark/{bm_id}", response_model=BenchmarkResponse)
def get_benchmark(
    bm_id: int,
    db: Session = Depends(get_db),
    current_user: UserPrincipal = Depends(require_role("viewer")),
) -> BenchmarkResponse:
    r = db.query(BenchmarkRecord).filter(BenchmarkRecord.id == bm_id).first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benchmark record not found.")

    raw_res = json.loads(r.results) if r.results else []
    model_results = [BenchmarkModelResult(**m) for m in raw_res]

    return BenchmarkResponse(
        id=r.id,
        prompt=r.prompt,
        results=model_results,
        best_model=r.best_model,
        benchmarked_at=r.created_at,
    )
