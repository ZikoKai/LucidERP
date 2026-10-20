from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import get_db

from .schemas import ActionRead, ProposeRequest
from .service import list_actions, propose

router = APIRouter()


@router.post("/agent/propose", response_model=ActionRead, status_code=201)
def propose_action(data: ProposeRequest, db: Session = Depends(get_db)):
    return propose(db, data.text)


@router.get("/agent-actions", response_model=list[ActionRead])
def actions(
    statut: Literal["proposee", "approuvee", "rejetee"] | None = None,
    db: Session = Depends(get_db),
):
    return list_actions(db, statut)
