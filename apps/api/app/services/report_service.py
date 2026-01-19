from __future__ import annotations

from datetime import datetime, timezone


def build_summary(payload: dict) -> dict:
    return {
        "status": payload.get("situacao", "INDEFINIDO"),
        "legal_name": payload.get("razao_social"),
        "document": payload.get("cnpj"),
        "snapshot_at": payload.get("consulta_em", datetime.now(timezone.utc).isoformat()),
    }
