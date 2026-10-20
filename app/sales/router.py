from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core import get_db

from .schemas import OrderCreate, OrderRead
from .service import create_order, get_order, list_orders

router = APIRouter()


@router.post("/orders", response_model=OrderRead, status_code=201)
def add_order(data: OrderCreate, db: Session = Depends(get_db)):
    order = create_order(db, data)
    db.commit()
    return order


@router.get("/orders", response_model=list[OrderRead])
def orders(
    statut: Literal["brouillon", "validee", "facturee"] | None = None,
    contact_id: int | None = None,
    min_risk: int | None = Query(default=None, ge=0, le=100),
    db: Session = Depends(get_db),
):
    return list_orders(db, statut, contact_id, min_risk)


@router.get("/orders/{order_id}", response_model=OrderRead)
def order(order_id: int, db: Session = Depends(get_db)):
    return get_order(db, order_id)
