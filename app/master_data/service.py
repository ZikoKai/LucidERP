from fastapi import HTTPException
from sqlalchemy import select

from .models import Contact, Product


def get_contact(db, contact_id):
    obj = db.get(Contact, contact_id)
    if obj is None:
        raise HTTPException(404, "Contact not found")
    return obj


def get_product(db, product_id):
    obj = db.get(Product, product_id)
    if obj is None:
        raise HTTPException(404, "Product not found")
    return obj


def list_contacts(db):
    return db.scalars(select(Contact).order_by(Contact.id)).all()


def list_products(db):
    return db.scalars(select(Product).order_by(Product.id)).all()


def create_contact(db, data):
    obj = Contact(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_product(db, data):
    obj = Product(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
