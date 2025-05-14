"""Module for loading initial sample data into the database."""

import json
import os
from pathlib import Path
from typing import List, Dict, Any

from db.registry import DatabaseRegistry
from db.entities.category import Category
from db.entities.product import Product


def load_json_data(filename: str) -> List[Dict[str, Any]]:
    """Load data from a JSON file."""
    # Primero intentamos buscar en /code/data (dentro del contenedor Docker)
    data_path = Path("/code/data") / filename
    if os.path.exists(data_path):
        print(f"Cargando datos desde {data_path}")
    else:
        # Si no existe, intentamos buscarlo en data/ (desarrollo local)
        data_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))) / "data" / filename
        if not os.path.exists(data_path):
            print(f"Warning: Data file {filename} not found at {data_path}")
            return []

    print(f"Cargando datos desde: {data_path}")
    with open(data_path, "r", encoding="utf-8") as file:
        return json.load(file)


def import_categories() -> None:
    """Import categories from JSON file."""
    session = DatabaseRegistry.session()

    # Verificar si ya existen categorías para evitar duplicados
    existing_count = session.query(Category).count()
    if existing_count > 0:
        print(f"Ya existen {existing_count} categorías. Saltando importación.")
        return

    categories_data = load_json_data("categories.json")
    for category_data in categories_data:
        category = Category(**category_data)
        session.add(category)

    session.commit()
    print(f"Importadas {len(categories_data)} categorías.")


def import_products() -> None:
    """Import products from JSON file."""
    session = DatabaseRegistry.session()

    # Verificar si ya existen productos para evitar duplicados
    existing_count = session.query(Product).count()
    if existing_count > 0:
        print(f"Ya existen {existing_count} productos. Saltando importación.")
        return

    products_data = load_json_data("products.json")
    for product_data in products_data:
        product = Product(**product_data)
        session.add(product)

    session.commit()
    print(f"Importados {len(products_data)} productos.")


def load_sample_data() -> None:
    """Load all sample data into the database."""
    print("Iniciando carga de datos de muestra...")
    try:
        import_categories()
        import_products()
        print("Carga de datos de muestra completada.")
    except Exception as e:
        print(f"Error durante la carga de datos de muestra: {e}")
        print("Continuando con la inicialización de la aplicación...")
