# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

eval-history-rerun

## Roadmap

### eval-history-rerun — Rerun Evaluation from History

Status: done

Acceptance:
- History list in EvaluateView shows a rerun button for each item
- Clicking rerun populates the form with that prompt and domain
- Clicking rerun triggers a new evaluation automatically
- Loading state shown during rerun evaluation

Implementation: `frontend/src/components/EvaluateView.tsx`, `frontend/src/styles.css`

Tests: `frontend/tests/EvaluateView.test.tsx`

