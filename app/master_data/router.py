from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import get_db

from . import service
from .schemas import ContactCreate, ContactRead, ProductCreate, ProductRead

router = APIRouter()


@router.post("/contacts", response_model=ContactRead, status_code=201)
def add_contact(data: ContactCreate, db: Session = Depends(get_db)):
    return service.create_contact(db, data)


@router.get("/contacts", response_model=list[ContactRead])
def contacts(db: Session = Depends(get_db)):
    return service.list_contacts(db)


@router.get("/contacts/{contact_id}", response_model=ContactRead)
def contact(contact_id: int, db: Session = Depends(get_db)):
    return service.get_contact(db, contact_id)


@router.post("/products", response_model=ProductRead, status_code=201)
def add_product(data: ProductCreate, db: Session = Depends(get_db)):
    return service.create_product(db, data)


@router.get("/products", response_model=list[ProductRead])
def products(db: Session = Depends(get_db)):
    return service.list_products(db)


@router.get("/products/{product_id}", response_model=ProductRead)
def product(product_id: int, db: Session = Depends(get_db)):
    return service.get_product(db, product_id)
