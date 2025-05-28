import os
import logging
import pymysql
from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import DatabaseRegistry, Category, Product
import fastapi_backend_template

# Configuración básica del logger
logger = logging.getLogger("ecommerce")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(console_handler)

app = FastAPI(title="E-commerce Search API")


DB_HOST = os.getenv("DB_HOST", "db")
DB_USER = os.getenv("DB_USER", "ecomuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "ecompass")
DB_NAME = os.getenv("DB_NAME", "ecommerce")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Inicio de la aplicacion")
    DatabaseRegistry.inicializar()
    DatabaseRegistry()
