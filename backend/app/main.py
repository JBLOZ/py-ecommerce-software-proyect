import os
import logging
import pymysql
from fastapi import FastAPI

app = FastAPI(title="E-commerce Search API")

DB_HOST = os.getenv("DB_HOST", "db")
DB_USER = os.getenv("DB_USER", "ecomuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "ecompass")
DB_NAME = os.getenv("DB_NAME", "ecommerce")
