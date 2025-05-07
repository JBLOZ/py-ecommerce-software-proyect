"""Database registry for managing database connections and sessions."""

import os
from typing import Optional

from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine


class DatabaseRegistry:
    """Registers and manages the database session."""

    DB_HOST = os.getenv("DB_HOST", "db")
    DB_USER = os.getenv("DB_USER", "ecomuser")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "ecompass")
    DB_NAME = os.getenv("DB_NAME", "ecommerce")
    __session: Optional[Session] = None

    @classmethod
    def session(cls) -> Session:
        """Returns the database session singleton."""
        if cls.__session is None:
            cls.__session = cls.__create_session()
        return cls.__session

    @classmethod
    def __get_engine(cls) -> Engine:
        """Returns the engine for the database."""
        return create_engine(
            f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}/{cls.DB_NAME}",
            echo=True,
        )

    @classmethod
    def __create_session(cls) -> Session:
        """Creates and returns a new database session."""
        engine = cls.__get_engine()
        # crear tablas si no existen
        SQLModel.metadata.create_all(engine)
        return Session(engine)
