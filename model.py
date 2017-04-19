# coding: utf-8

from sqlalchemy import Column, Integer, ForeignKey, Float, Boolean, String
from sqlalchemy.orm import mapper, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Character(Base):
    __tablename__ = 'characters'
    id = Column(Integer, primary_key=True)
    aliases = relationship("Alias", back_populates="character")
    name = Column(String)

    def __repr__(self):
        return "<chr%s>" % self.id


class Alias(Base):
    __tablename__ = 'aliases'
    id = Column(Integer, primary_key=True)

    character_id = Column(Integer, ForeignKey('characters.id'))
    character = relationship("Character", back_populates="aliases")
