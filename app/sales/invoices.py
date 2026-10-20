from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import get_db

from .models import Invoice, SalesOrder
from .schemas import InvoiceRead
from .service import get_order

router = APIRouter()


@router.post("/orders/{order_id}/invoice", response_model=InvoiceRead, status_code=201)
def generate_invoice(order_id: int, db: Session = Depends(get_db)):
    order = get_order(db, order_id)
    changed = db.execute(
        update(SalesOrder)
        .where(
            SalesOrder.id == order_id,
            SalesOrder.statut == "validee",
        )
        .values(statut="facturee")
    )
    if changed.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "Only validated orders without an invoice may be invoiced")
    total = sum((line.prix_unitaire * line.quantite for line in order.lines), Decimal("0"))
    invoice = Invoice(order_id=order_id, montant_total=total)
    db.add(invoice)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Order already invoiced") from None
    db.refresh(invoice)
    return invoice


@router.get("/invoices", response_model=list[InvoiceRead])
def invoices(db: Session = Depends(get_db)):
    return db.scalars(select(Invoice).order_by(Invoice.id)).all()
