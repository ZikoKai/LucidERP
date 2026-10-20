from decimal import Decimal

from sqlalchemy import CheckConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = (CheckConstraint("type IN ('client', 'fournisseur')"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str]
    type: Mapped[str] = mapped_column(default="client")
    email: Mapped[str] = mapped_column(default="")
    ville: Mapped[str] = mapped_column(default="")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (CheckConstraint("prix_unitaire >= 0 AND stock_declare >= 0"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str]
    prix_unitaire: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    stock_declare: Mapped[int] = mapped_column(default=0)
