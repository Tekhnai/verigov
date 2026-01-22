from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.check_service import run_cnpj_check


def test_healthz(client: TestClient):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    body = resp.json()
    assert "status" in body
    assert "db" in body and "redis" in body  # may be degraded if redis not reachable
    # request id should be returned
    assert "x-request-id" in resp.headers


def test_auth_register_login_refresh(client: TestClient):
    payload = {"email": "user@example.com", "password": "Pass1234!", "tenant_name": "tenantx"}
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 200
    tokens = resp.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    resp_login = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert resp_login.status_code == 200
    tokens_login = resp_login.json()
    assert tokens_login["access_token"]

    resp_refresh = client.post("/auth/refresh", json={"refresh_token": tokens_login["refresh_token"]})
    assert resp_refresh.status_code == 200
    refreshed = resp_refresh.json()
    assert refreshed["access_token"]
    assert refreshed["refresh_token"]


def test_target_check_and_report(client: TestClient, db_session: Session):
    # Register and login
    reg = client.post(
        "/auth/register",
        json={"email": "target@example.com", "password": "Pass1234!", "tenant_name": "acme"},
    )
    assert reg.status_code == 200
    access = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {access}"}

    # Create target
    resp_target = client.post("/targets", json={"document": "12345678000190", "name_hint": "ACME", "type": "cnpj"}, headers=headers)
    assert resp_target.status_code == 201
    target_id = resp_target.json()["id"]

    # Run check (sync mocked)
    resp_check = client.post(f"/targets/{target_id}/check", headers=headers)
    assert resp_check.status_code == 200
    summary = resp_check.json()["summary"]
    assert summary["status"]
    assert summary["source"]

    # Fetch report/latest
    resp_report = client.get(f"/targets/{target_id}/report/latest", headers=headers)
    assert resp_report.status_code == 200
    latest = resp_report.json()
    assert latest["summary_json"]["status"]


def test_metrics_endpoint(client: TestClient):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert resp.text  # non-empty
