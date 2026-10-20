from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProposalLine(BaseModel):
    product_id: int = Field(gt=0)
    quantite: int = Field(gt=0, le=1_000_000)


class StructuredProposal(BaseModel):
    contact_id: int = Field(gt=0)
    lines: list[ProposalLine] = Field(min_length=1, max_length=100)
    reasoning: str

    @model_validator(mode="after")
    def distinct_products(self):
        if len({line.product_id for line in self.lines}) != len(self.lines):
            raise ValueError("Each product may occur only once per proposal")
        return self


class ProposeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class DecisionRequest(BaseModel):
    decide_par: str = Field(min_length=1, max_length=200, pattern=r"\S")


class ActionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_id: int | None
    acteur: str
    action: str
    raisonnement: str
    timestamp: datetime
    statut: Literal["proposee", "approuvee", "rejetee"]
    payload: dict
    risk_score: int
    risk_explanation: str
    decide_par: str | None
    decide_le: datetime | None
