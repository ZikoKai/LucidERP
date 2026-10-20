from datetime import date as Date
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base


class SalesOrder(Base):
    __tablename__ = "sales_orders"
    __table_args__ = (CheckConstraint("statut IN ('brouillon', 'validee', 'facturee')"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"))
    date: Mapped[Date] = mapped_column(default=Date.today)
    statut: Mapped[str] = mapped_column(default="brouillon")
    risk_score: Mapped[int] = mapped_column(default=0)
    risk_explanation: Mapped[str]
    lines: Mapped[list["SalesOrderLine"]] = relationship(cascade="all, delete-orphan")


class SalesOrderLine(Base):
    __tablename__ = "sales_order_lines"
    __table_args__ = (CheckConstraint("quantite > 0 AND prix_unitaire >= 0"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("sales_orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantite: Mapped[int]
    prix_unitaire: Mapped[Decimal] = mapped_column(Numeric(14, 2))


class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("sales_orders.id"), unique=True)
    date: Mapped[Date] = mapped_column(default=Date.today)
    montant_total: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    statut: Mapped[str] = mapped_column(default="emise")
