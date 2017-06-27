# coding: utf-8

from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

session = None


class Character(Base):
    __tablename__ = 'characters'
    id = Column(Integer, primary_key=True)
    aliases = relationship("Alias", back_populates="character")
    name = Column(String)

    words = relationship("Word", back_populates="character")

    def __repr__(self):
        return "<chr%s %s %s>" % (self.id, self.name, self.aliases)

    def seek_next_unmarked(self):
        if ' ' in self.name:
            parts = self.name.split(' ')
            w = session.query(
                Word).filter(
                    Word.word.like('%'+parts[0]+'%')).filter(
                        Word.character == None
                    ).first()
            if w is None:
                return []
            else:
                return [w, ] + [session.query(Word).get(w.id + n)
                                for n in range(1, len(parts))]
        else:
            w = session.query(
                Word).filter(
                    Word.word.like('%'+self.name+'%')).filter(
                        Word.character == None
                    ).first()
            if w:
                return [w, ]
            else:
                return []

    def mark_all(self):
        while self.seek_next_unmarked():
            for w in self.seek_next_unmarked():
                print w
                w.character = self
                session.commit()


class Alias(Base):
    __tablename__ = 'aliases'
    id = Column(Integer, primary_key=True)

    alias = Column(String)
    character_id = Column(Integer, ForeignKey('characters.id'))
    character = relationship("Character", back_populates="aliases")

    def __repr__(self):
        return "<alias %s of %s>" % (self.alias, self.character.name)


class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    word = Column(String)
    pos = Column(String)

    sentence_id = Column(Integer, ForeignKey('sentences.id'))
    sentence = relationship("Sentence", back_populates="words")

    character_id = Column(Integer, ForeignKey('characters.id'), nullable=True)
    character = relationship("Character", back_populates="words")

    def __repr__(self):
        return "<w%s %s %s>" % (self.id, self.pos, self.word)


class Sentence(Base):
    __tablename__ = 'sentences'
    id = Column(Integer, primary_key=True)
    sentence = Column(String)
    words = relationship("Word", back_populates="sentence")

    def __repr__(self):
        return "<s%s '%s'>" % (self.id, self.sentence)

    def set_word_coords(self):
        offset = 0
        y = 3
        x = 0
        for w in self.words:
            y = 3 + offset / 70
            x = offset % 70
            #if y > 3:
            #    x -= 1

            w.x = x
            w.y = y

            offset += len(w.word) + 1
