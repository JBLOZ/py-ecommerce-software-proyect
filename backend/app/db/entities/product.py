""" Product entity representation for SQLAlchemy ORM. """

from typing import Optional
from sqlmodel import SQLModel, Field


class Product(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int = Field(primary_key=True)
    name: str
    description: Optional[str] = None
    price: float
    category_id: int = Field(foreign_key="category.id")
