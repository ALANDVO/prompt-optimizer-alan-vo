from fastapi.testclient import TestClient


def test_health_and_version(client: TestClient):
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_ver = client.get("/api/version")
    assert res_ver.status_code == 200
    assert "version" in res_ver.json()


def test_auth_oidc_config(client: TestClient):
    res = client.get("/api/auth/config")
    assert res.status_code == 200
    data = res.json()
    assert "issuer_url" in data
    assert "client_id" in data
    assert "audience" in data
    assert data["demo_mode"] is True


def test_auth_demo_login_and_token_propagation(client: TestClient):
    login_res = client.post("/api/auth/demo-login", json={"username": "alice", "role": "operator"})
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    token = login_data["access_token"]

    # Use token in authorized API request
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["username"] == "alice"
    assert "operator" in me_data["roles"]


def test_evaluate_api_workflow(client: TestClient, viewer_headers: dict[str, str]):
    eval_payload = {
        "prompt": "You are a cloud architect. Create an AWS ECS deployment checklist with strict JSON schema output.",
        "domain": "software_engineering",
    }
    create_res = client.post("/api/evaluate", headers=viewer_headers, json=eval_payload)
    assert create_res.status_code == 200
    eval_data = create_res.json()
    assert "id" in eval_data
    eval_id = eval_data["id"]
    assert eval_data["overall_score"] > 0
    assert len(eval_data["dimensions"]) == 8

    # Fetch record
    get_res = client.get(f"/api/evaluations/{eval_id}", headers=viewer_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == eval_id


def test_optimize_api_workflow(client: TestClient, operator_headers: dict[str, str], viewer_headers: dict[str, str]):
    opt_payload = {
        "prompt": "Review code for SQL injection vulnerabilities",
        "target_domain": "cybersecurity",
        "strategy": "structured",
        "use_advisory_llm": False,
    }
    opt_res = client.post("/api/optimize", headers=operator_headers, json=opt_payload)
    assert opt_res.status_code == 200
    opt_data = opt_res.json()
    assert opt_data["score_after"] > opt_data["score_before"]
    opt_id = opt_data["id"]

    # Verify retrieval
    get_res = client.get(f"/api/optimizations/{opt_id}", headers=viewer_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == opt_id


def test_ab_test_api_workflow(client: TestClient, operator_headers: dict[str, str], viewer_headers: dict[str, str]):
    ab_payload = {
        "prompt_a": "You are a senior analyst. Return only JSON format with keys status and summary.",
        "prompt_b": "Tell me what happened in plain English.",
        "cases": [
            {"input": "Server reboot incident", "expected": "json", "assertion_type": "contains"},
            {"input": "High memory consumption", "expected": "status", "assertion_type": "contains"},
        ],
    }
    res = client.post("/api/ab-test", headers=operator_headers, json=ab_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["winner"] == "A"
    assert data["cases_count"] == 2
    ab_id = data["id"]

    get_res = client.get(f"/api/ab-tests/{ab_id}", headers=viewer_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == ab_id


def test_benchmark_api_workflow(client: TestClient, operator_headers: dict[str, str], viewer_headers: dict[str, str]):
    bm_payload = {
        "prompt": "Evaluate prompt quality across latency and compliance profiles.",
        "models": ["gpt-4o-mini", "claude-3-5-sonnet"],
    }
    res = client.post("/api/benchmark", headers=operator_headers, json=bm_payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["results"]) == 2
    bm_id = data["id"]

    get_res = client.get(f"/api/benchmarks/{bm_id}", headers=viewer_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == bm_id


def test_prompt_crud_lifecycle(client: TestClient, operator_headers: dict[str, str], admin_headers: dict[str, str], viewer_headers: dict[str, str]):
    # 1. Create
    create_payload = {
        "name": "Kubernetes Ingress Architect",
        "prompt": "Design ingress configuration with TLS termination and rate limits.",
        "domain": "software_engineering",
        "tags": "k8s,devops,networking",
    }
    create_res = client.post("/api/prompts", headers=operator_headers, json=create_payload)
    assert create_res.status_code == 201
    prompt_id = create_res.json()["id"]

    # 2. Read
    get_res = client.get(f"/api/prompts/{prompt_id}", headers=viewer_headers)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Kubernetes Ingress Architect"

    # 3. Update
    update_res = client.put(
        f"/api/prompts/{prompt_id}",
        headers=operator_headers,
        json={"prompt": "Updated ingress instructions with WAF annotations."},
    )
    assert update_res.status_code == 200
    assert update_res.json()["version"] == 2

    # 4. Delete
    del_res = client.delete(f"/api/prompts/{prompt_id}", headers=admin_headers)
    assert del_res.status_code == 200

    # 5. Confirm Deleted
    not_found_res = client.get(f"/api/prompts/{prompt_id}", headers=viewer_headers)
    assert not_found_res.status_code == 404


def test_admin_audit_logs_access(client: TestClient, admin_headers: dict[str, str], viewer_headers: dict[str, str]):
    # Viewer forbidden from accessing audit logs
    viewer_res = client.get("/api/audit-logs", headers=viewer_headers)
    assert viewer_res.status_code == 403

    # Admin allowed to access audit logs
    admin_res = client.get("/api/audit-logs", headers=admin_headers)
    assert admin_res.status_code == 200
    data = admin_res.json()
    assert "items" in data
    assert "total" in data
