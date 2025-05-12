import os
import logging
import pymysql
from fastapi import FastAPI, HTTPException, Body
from sqlmodel import select
from backend.app.db.registry import DatabaseRegistry
from backend.app.db.entities.category import Category
from backend.app.db.entities.product import Product

app = FastAPI(title="E-commerce Search API")

DB_HOST = os.getenv("DB_HOST", "db")
DB_USER = os.getenv("DB_USER", "ecomuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "ecompass")
DB_NAME = os.getenv("DB_NAME", "ecommerce")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/categories")
def get_categories():
    session = DatabaseRegistry.session()
    categories = session.exec(select(Category)).all()
    return {"categories": [{"id": c.id, "name": c.name} for c in categories]}


@app.get("/products")
def get_products():
    session = DatabaseRegistry.session()
    products = session.exec(select(Product)).all()
    return {"products": [{"id": p.id, "name": p.name, "price": p.price} for p in products]}


@app.post("/search/text")
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
