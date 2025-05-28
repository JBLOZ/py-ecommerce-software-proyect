""" Product entity representation for SQLAlchemy ORM. """

from sqlmodel import SQLModel, Field
from typing import Optional

class Product(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str 
    description: Optional[str] = None
    category_id: int = Field(foreign_key="category.id")
