"""Database registry for managing database connections and sessions."""

import os
from typing import Optional

from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine


class DatabaseRegistry:
    """Registers and manages the database session."""

    DB_HOST = os.getenv("DB_HOST", "db")
    DB_USER = os.getenv("DB_USER", "user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("DB_NAME", "ecommerce")
    __session: Optional[Session] = None
    __engine: Optional[Engine] = None
    __db_url: Optional[str] = None

    @classmethod
    def initialize(cls, db_url: Optional[str] = None) -> None:
        """Initialize the database connection."""
        if db_url:
            cls.__db_url = db_url
        cls.__engine = cls.__get_engine()
        # Crear tablas si no existen
        SQLModel.metadata.create_all(cls.__engine)
        cls.__session = Session(cls.__engine)
        print("Base de datos inicializada correctamente.")

    @classmethod
    def close(cls) -> None:
        """Close the database session."""
        if cls.__session:
            cls.__session.close()
            cls.__session = None
        if cls.__engine:
            cls.__engine.dispose()
            cls.__engine = None
        print("Conexiones a la base de datos cerradas correctamente.")

    @classmethod
    def session(cls) -> Session:
        """Returns the database session singleton."""
        if cls.__session is None:
            cls.__session = cls.__create_session()
        return cls.__session

    @classmethod
    def __get_engine(cls) -> Engine:
        """Returns the engine for the database."""
        if cls.__db_url:
            return create_engine(cls.__db_url, echo=True)
        return create_engine(
            f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}/{cls.DB_NAME}",
            echo=True,
        )

    @classmethod
    def __create_session(cls) -> Session:
        """Creates and returns a new database session."""
        engine = cls.__get_engine()
        # Crear tablas si no existen
        SQLModel.metadata.create_all(engine)
        return Session(engine)
