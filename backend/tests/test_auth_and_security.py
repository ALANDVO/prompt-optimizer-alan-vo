import pytest
from fastapi.testclient import TestClient
from app.core.config import Settings
from app.core.security import create_demo_token, decode_token, UserPrincipal
from app.core.audit import record_audit


def test_demo_token_issuance_and_roles():
    token = create_demo_token("analyst_user", "operator")
    principal = decode_token(token)

    assert principal.username == "analyst_user"
    assert principal.has_role("operator") is True
    assert principal.has_role("viewer") is True
    assert principal.has_role("admin") is False
    assert principal.is_demo is True


def test_unauthenticated_request_rejected(client: TestClient):
    response = client.get("/api/prompts")
    assert response.status_code == 401
    assert "detail" in response.json()


def test_invalid_token_rejected(client: TestClient):
    response = client.get("/api/prompts", headers={"Authorization": "Bearer invalid.fake.token"})
    assert response.status_code == 401


def test_role_hierarchy_authorization(client: TestClient, viewer_headers: dict[str, str], operator_headers: dict[str, str], admin_headers: dict[str, str]):
    # Viewer can read prompts
    res_viewer_read = client.get("/api/prompts", headers=viewer_headers)
    assert res_viewer_read.status_code == 200

    # Viewer cannot create prompt (requires operator)
    res_viewer_create = client.post(
        "/api/prompts",
        headers=viewer_headers,
        json={"name": "Forbidden Test Prompt", "prompt": "Some prompt", "domain": "general"},
    )
    assert res_viewer_create.status_code == 403

    # Operator can create prompt
    res_op_create = client.post(
        "/api/prompts",
        headers=operator_headers,
        json={"name": "Operator Created Prompt", "prompt": "Some prompt text", "domain": "general"},
    )
    assert res_op_create.status_code == 201
    created_id = res_op_create.json()["id"]

    # Operator cannot delete prompt (requires admin)
    res_op_delete = client.delete(f"/api/prompts/{created_id}", headers=operator_headers)
    assert res_op_delete.status_code == 403

    # Admin can delete prompt
    res_admin_delete = client.delete(f"/api/prompts/{created_id}", headers=admin_headers)
    assert res_admin_delete.status_code == 200


def test_production_demo_mode_refusal():
    # Verify that demo mode is refused in production
    settings = Settings(environment="production", demo_mode=True)
    with pytest.raises(RuntimeError) as exc_info:
        settings.validate_environment()
    assert "DEMO_MODE must not be enabled when ENVIRONMENT is production" in str(exc_info.value)


def test_secret_redaction_in_audit_logs(db_session):
    # Construct a synthetic secret at runtime without token-shaped patterns
    synthetic_key = "synthetic_key_" + ("0" * 32)
    entry = record_audit(
        db_session,
        user_id="user-123",
        username="auditor",
        action="update_config",
        resource="config",
        details={"api_key": synthetic_key, "safe_field": "public_data"},
    )
    assert "[REDACTED]" in entry.details
    assert synthetic_key not in entry.details
    assert "public_data" in entry.details
