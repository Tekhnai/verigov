from __future__ import annotations

from datetime import datetime, timezone

import httpx


def _mock_response(cnpj: str) -> dict:
    return {
        "cnpj": cnpj,
        "razao_social": "ACME TECNOLOGIA LTDA",
        "situacao": "ATIVA",
        "abertura": "2012-05-14",
        "consulta_em": datetime.now(timezone.utc).isoformat(),
    }


def fetch_cnpj(cnpj: str, use_mock: bool = False) -> dict:
    if use_mock:
        return _mock_response(cnpj)

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"https://publica.cnpj.ws/cnpj/{cnpj}")
            resp.raise_for_status()
            data = resp.json()
            return {
                "cnpj": cnpj,
                "razao_social": data.get("razao_social"),
                "situacao": data.get("estabelecimento", {}).get("situacao_cadastral"),
                "abertura": data.get("estabelecimento", {}).get("data_inicio_atividade"),
                "consulta_em": datetime.now(timezone.utc).isoformat(),
            }
    except Exception:
        return _mock_response(cnpj)
