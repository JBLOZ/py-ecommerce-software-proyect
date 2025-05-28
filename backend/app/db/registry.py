"""Database registry for managing database connections and sessions."""

import os
from typing import Optional
import logging
from sqlalchemy import Engine
from sqlmodel import create_engine, Session

logger = logging.getLogger("registry_logger")
logger.setLevel(logging.INFO)
handle = logging.StreamHandler()
handle.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(handle)


class DatabaseRegistry:
    """Registers and manages the database session."""

    DB_HOST = os.getenv("DB_HOST", "db")
    DB_USER = os.getenv("DB_USER", "ecomuser")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "ecompass")
    DB_NAME = os.getenv("DB_NAME", "ecommerce")
    __session: Optional[Session] = None

    @staticmethod
    @property
    def session() -> Session:
        """Returns the database session."""
        if DatabaseRegistry.__session is None:
            DatabaseRegistry.__session = DatabaseRegistry.__create_session()
        return DatabaseRegistry.__session

    @classmethod
    def __get_engine(cls) -> Engine:
        """Returns the engine for the database."""
        return create_engine(
            f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}/{cls.DB_NAME}",
            echo=True,
        )

    @classmethod
    def __create_session(cls) -> Session:
        """Returns the session for the database."""
        cls.session = Session(cls.__get_engine())

    @classmethod
    def inicializar(cls, sql_path):
        """Inicializa la base de datos ejecutando el script init.sql."""
        try:
            with open(sql_path, "r", encoding="utf-8") as f:
                sql_script = f.read()
            engine = cls.__get_engine()

            with engine.connect() as conn:
                conn.exec_driver_sql(sql_script, execution_options={"autocommit": True})

        except Exception as e:
            logger.exception(f"Excepcion ejecutando {sql_path}: {e}")
