from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.common.explainability import score_risk
from app.master_data import get_contact, get_product

from .models import SalesOrder, SalesOrderLine


def get_order(db, order_id):
    order = db.get(SalesOrder, order_id)
    if order is None:
        raise HTTPException(404, "Order not found")
    return order


def list_orders(db, statut=None, contact_id=None, min_risk=None):
    query = select(SalesOrder).options(selectinload(SalesOrder.lines)).order_by(SalesOrder.id)
    if statut is not None:
        query = query.where(SalesOrder.statut == statut)
    if contact_id is not None:
        query = query.where(SalesOrder.contact_id == contact_id)
    if min_risk is not None:
        query = query.where(SalesOrder.risk_score >= min_risk)
    return db.scalars(query).all()


def assess_order(db, contact_id, lines):
    """Read-only public API shared by human orders and agent proposals."""
    if get_contact(db, contact_id).type != "client":
        raise HTTPException(422, "Sales orders require a client contact")
    priced_lines = []
    total = Decimal("0")
    stocks = []
    for line in lines:
        product = get_product(db, line.product_id)
        total += product.prix_unitaire * line.quantite
        stocks.append((line.quantite, product.stock_declare))
        priced_lines.append(
            dict(
                product_id=product.id,
                quantite=line.quantite,
                prix_unitaire=str(product.prix_unitaire),
            )
        )
    if total > Decimal("999999999999.99"):
        raise HTTPException(422, "Order total exceeds supported monetary precision")
    past_totals = [
        sum((row.prix_unitaire * row.quantite for row in order.lines), Decimal("0"))
        for order in list_orders(db, contact_id=contact_id)
    ]
    score, explanation = score_risk(total, past_totals, stocks)
    return priced_lines, score, explanation


def create_order(db, data):
    """Stage an order; caller owns the transaction and commits atomically."""
    lines, score, explanation = assess_order(db, data.contact_id, data.lines)
    order = SalesOrder(
        contact_id=data.contact_id,
        statut=data.statut,
        risk_score=score,
        risk_explanation=explanation,
        lines=[
            SalesOrderLine(**{**line, "prix_unitaire": Decimal(line["prix_unitaire"])})
            for line in lines
        ],
    )
    db.add(order)
    db.flush()
    return order
