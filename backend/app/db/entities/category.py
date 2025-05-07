""" Category entity representation for SQLAlchemy ORM. """

from enum import Enum


class CategoryTypes(Enum):
    """ Enum for category types. """
    CAMISETAS = 1
    TELEFONOS = 2
    PANTALONES = 3
    ZAPATOS = 4
    PORTATILES = 5
    OTROS = 6
