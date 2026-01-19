from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.utils import normalize_cnpj


class TargetCreate(BaseModel):
    document: str
    name_hint: str | None = None
    type: str = Field(default="CNPJ")

    @field_validator("document")
    @classmethod
    def validate_document(cls, value: str) -> str:
        return normalize_cnpj(value)


class TargetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    document: str
    name_hint: str | None
    type: str
    created_at: datetime
