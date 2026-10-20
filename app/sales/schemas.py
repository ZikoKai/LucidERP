from datetime import date as Date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LineCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantite: int = Field(gt=0, le=1_000_000)


class OrderCreate(BaseModel):
    contact_id: int = Field(gt=0)
    statut: Literal["brouillon", "validee"] = "brouillon"
    lines: list[LineCreate] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def distinct_products(self):
        if len({line.product_id for line in self.lines}) != len(self.lines):
            raise ValueError("Each product may occur only once per order")
        return self


class LineRead(LineCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    prix_unitaire: Decimal


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    contact_id: int
    date: Date
    statut: str
    risk_score: int
    risk_explanation: str
    lines: list[LineRead]


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_id: int
    date: Date
    montant_total: Decimal
    statut: str
