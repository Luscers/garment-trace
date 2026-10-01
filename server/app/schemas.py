from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class TraceFactory(BaseModel):
    name: str
    brand: str
    address: str
    license_no: str = ""
    contact: str = ""
    phone: str = ""
    intro: str = ""


class TraceProduct(BaseModel):
    style_no: str
    name: str
    category: str = ""
    composition: str = ""
    standard_no: str = ""
    color: str = ""
    size_range: str = ""
    care: str = ""


class TraceBatch(BaseModel):
    batch_no: str
    production_date: date | None = None
    inspector: str = ""
    workshop: str = ""
    grade: str = "合格"


class TraceCard(BaseModel):
    code: str
    verified: bool = True
    queried_at: datetime
    factory: TraceFactory
    product: TraceProduct
    batch: TraceBatch
    timeline: list[dict[str, Any]] = Field(default_factory=list)


class ApiMessage(BaseModel):
    code: int = 0
    message: str = "ok"
    data: Any = None


class LoginRequest(BaseModel):
    username: str
    password: str


class CodeToggle(BaseModel):
    status: str
