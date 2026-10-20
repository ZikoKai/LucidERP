from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ContactCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=200)
    type: Literal["client", "fournisseur"] = "client"
    email: str = ""
    ville: str = ""


class ContactRead(ContactCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ProductCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=200)
    prix_unitaire: Decimal = Field(default=Decimal("0"), ge=0, max_digits=14, decimal_places=2)
    stock_declare: int = Field(default=0, ge=0)


class ProductRead(ProductCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
