"""Run from the repository root: python scripts/seed.py."""

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.core.db import SessionLocal  # noqa: E402
from app.master_data.models import Contact, Product  # noqa: E402
from app.sales import OrderCreate, create_order  # noqa: E402


def main():
    with SessionLocal() as db:
        if db.scalar(select(Contact.id).limit(1)) is not None:
            print("Seed skipped: contacts already exist. Use a fresh database for demo data.")
            return
        acme = Contact(nom="Acme", email="hello@acme.example", ville="Casablanca")
        nova = Contact(nom="Nova", ville="Rabat")
        supplier = Contact(nom="Papeterie Atlas", type="fournisseur")
        pens = Product(nom="stylos", prix_unitaire=Decimal("10.00"), stock_declare=20)
        desk = Product(nom="bureau", prix_unitaire=Decimal("600.00"), stock_declare=2)
        db.add_all([acme, nova, supplier, pens, desk])
        db.flush()
        create_order(
            db,
            OrderCreate(
                contact_id=acme.id,
                statut="validee",
                lines=[{"product_id": pens.id, "quantite": 10}],
            ),
        )
        create_order(
            db, OrderCreate(contact_id=acme.id, lines=[{"product_id": pens.id, "quantite": 40}])
        )
        db.commit()
    print(
        "Seeded Acme, Nova, stylos and bureau. Try '40 stylos pour Acme' or '3 bureau pour Nova'."
    )


if __name__ == "__main__":
    main()
