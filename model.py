# coding: utf-8

from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
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

    def from_words(self, words):
        self.name = " ".join([word.word for word in words])
        self.words = words

    def get_names(self):
        return [self.name, ] + [alias.alias for alias in self.aliases]

    def seek_unmarked_word(self):
        for name in self.get_names():
            if ' ' in name:
                parts = name.split(' ')
                w = session.query(
                    Word).filter(
                        Word.word.like('%'+parts[0]+'%')).filter(
                            Word.character == None
                        ).filter(
                            Word.ignore == False
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
                        ).filter(
                            Word.ignore == False
                        ).first()
                if w:
                    return [w, ]
                else:
                    return []

    def mark_all(self):
        while self.seek_unmarked_word():
            for w in self.seek_unmarked_word():
                w.character = self
                session.commit()


class Alias(Base):
    __tablename__ = 'aliases'
    id = Column(Integer, primary_key=True)

    alias = Column(String)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    character = relationship("Character", back_populates="aliases")

    def __repr__(self):
        return "<alias %s of %s>" % (self.alias, self.character.name)


class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    word = Column(String)
    pos = Column(String)

    ignore = Column(Boolean, default=False)

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


def seek_unmarked_name():
    w = session.query(Word).filter((Word.pos == 'NNP')
                                   | (Word.pos == 'NNPS'))\
                           .filter(Word.character == None)\
                           .filter(Word.ignore == False)\
                           .first()

    if w is None:
        return []
    else:
        nnp = [w, ]
        n = 1
        nextw = session.query(Word).get(w.id + n)
        while n < session.query(Word).count() and \
                nextw.pos == 'NNP' or nextw.pos == 'NNPS':
            nnp.append(nextw)
            n += 1
            nextw = session.query(Word).get(w.id + n)

        return nnp
