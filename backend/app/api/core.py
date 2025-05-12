from fastapi import APIRouter, Body
from sqlmodel import select
from db import DatabaseRegistry
from db import Category
from db import Product

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/categories")
def get_categories():
    session = DatabaseRegistry.session()
    categories = session.exec(select(Category)).all()
    return {"categories": [{"id": c.id, "name": c.name} for c in categories]}

@router.get("/products")
def get_products():
    session = DatabaseRegistry.session()
    products = session.exec(select(Product)).all()
    return {"products": [{"id": p.id, "name": p.name, "price": p.price} for p in products]}

@router.post("/search/text")
def search_text(payload: dict = Body(...)):
    query = payload.get("query", "").lower()
    session = DatabaseRegistry.session()
    # Buscar categorías por coincidencia de nombre
    all_cats = session.exec(select(Category)).all()
    matched = [c.name for c in all_cats if query and c.name.lower() in query]
    # Obtener productos de categorías coincidentes
    products = session.exec(select(Product)).all()
    filtered = [p for p in products if p.category_id in [c.id for c in all_cats if c.name in matched]]
    return {"categories": matched, "products": [{"id": p.id, "name": p.name, "price": p.price} for p in filtered]}
    filtered = [p for p in products if p.category_id in matched]
    return {"categories": [c.name for c in all_cats if c.id in matched],
            "products": [{"id": p.id, "name": p.name, "price": p.price} for p in filtered]}
