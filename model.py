# coding: utf-8

from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
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

    alias = Column(String)
    character_id = Column(Integer, ForeignKey('characters.id'))
    character = relationship("Character", back_populates="aliases")


# class Offset(Base):
#     __tablename__ = 'offsets'
#     id = Column(Integer, primary_key=True)

#     sentence_offset = Column(Integer)
#     word_offset = Column(Integer)

#     character_id = Column(Integer, ForeignKey('characters.id'))
#     character = relationship("Character", back_populates="aliases")


class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    word = Column(String)
    pos = Column(String)

    sentence_id = Column(Integer, ForeignKey('sentences.id'))
    sentence = relationship("Sentence", back_populates="words")

    def __repr__(self):
        return "<w%s %s %s>" % (self.id, self.pos, self.word)


class Sentence(Base):
    __tablename__ = 'sentences'
    id = Column(Integer, primary_key=True)
    sentence = Column(String)
    words = relationship("Word", back_populates="sentence")

    def __repr__(self):
        return "<s%s '%s'>" % (self.id, self.sentence)

    
