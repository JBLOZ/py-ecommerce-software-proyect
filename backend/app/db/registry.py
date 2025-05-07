"""Database registry for managing database connections and sessions."""

import os
from typing import Optional

from sqlalchemy import Engine
from sqlmodel import create_engine, Session


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
