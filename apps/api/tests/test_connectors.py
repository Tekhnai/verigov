from __future__ import annotations

import httpx
import pytest

from app.connectors import receita


class _FakeResponse:
    def __init__(self, data: dict, status_code: int = 200):
        self._data = data
        self.status_code = status_code

    def json(self) -> dict:
        return self._data

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                message="error",
                request=httpx.Request("GET", "https://example.com"),
                response=httpx.Response(self.status_code),
            )


class _FakeClient:
    def __init__(self, responses: list[_FakeResponse], by_url: dict[str, _FakeResponse] | None = None):
        self._responses = responses
        self._idx = 0
        self._by_url = by_url or {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def get(self, url: str):
        if self._by_url:
            return self._by_url.get(url, _FakeResponse({}, status_code=500))
        # Return sequential responses to simulate primary/fallback chain
        if self._idx >= len(self._responses):
            raise RuntimeError("No more fake responses")
        resp = self._responses[self._idx]
        self._idx += 1
        return resp


@pytest.fixture(autouse=True)
def disable_cache(monkeypatch):
    # Avoid touching Redis during connector tests
    monkeypatch.setattr(receita, "_get_redis", lambda: None)


def test_fetch_cnpj_primary_success(monkeypatch):
    fake_payload = {
        "razao_social": "Empresa X",
        "estabelecimento": {"situacao_cadastral": "ATIVA", "data_inicio_atividade": "2020-01-01"},
    }
    monkeypatch.setattr(
        receita.httpx,
        "Client",
        lambda *args, **kwargs: _FakeClient([_FakeResponse(fake_payload, 200)]),
    )

    data = receita.fetch_cnpj("12.345.678/0001-90", use_mock=False)
    assert data["source"] == "publica.cnpj.ws"
    assert data["razao_social"] == "Empresa X"
    assert data["situacao"] == "ATIVA"


def test_fetch_cnpj_fallback_to_brasilapi(monkeypatch):
    brasilapi_payload = {
        "razao_social": "Fallback SA",
        "descricao_situacao_cadastral": "INAPTA",
        "data_inicio_atividade": "2019-05-01",
    }

    def _fake_client(*args, **kwargs):
        by_url = {
            "https://publica.cnpj.ws/cnpj/12345678000190": _FakeResponse({}, status_code=500),
            "https://brasilapi.com.br/api/cnpj/v1/12345678000190": _FakeResponse(brasilapi_payload, 200),
        }
        return _FakeClient([], by_url=by_url)

    monkeypatch.setattr(receita.httpx, "Client", _fake_client)

    data = receita.fetch_cnpj("12345678000190", use_mock=False)
    assert data["source"] == "brasilapi"
    assert data["razao_social"] == "Fallback SA"
    assert data["situacao"] == "INAPTA"


def test_fetch_cnpj_mock_when_all_fail(monkeypatch):
    # All attempts raise HTTP error; mock should be returned when allowed
    monkeypatch.setattr(
        receita.httpx,
        "Client",
        lambda *args, **kwargs: _FakeClient(
            [
                _FakeResponse({}, status_code=500),
                _FakeResponse({}, status_code=500),
                _FakeResponse({}, status_code=500),
            ]
        ),
    )
    data = receita.fetch_cnpj("12345678000190", use_mock=False)
    assert data["source"] == "mock"
    assert data["cnpj"] == "12345678000190"
