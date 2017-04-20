import curses
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import model


################################
# parse command line arguments #
################################
parser = argparse.ArgumentParser(
    description='Character dictionary from plain text,' +
                'in a relational database')
parser.add_argument('--db_url',
                    default='sqlite:///characters.sqlite',
                    help='DB URL, default: sqlite:///characters.sqlite')
parser.add_argument('--distance',
                    default=120,
                    help='word distance to connect characters')
args = parser.parse_args()


####################
# database connect #
####################
engine = create_engine(args.db_url)
Session = sessionmaker(bind=engine)
session = Session()
model.session = session


class Tagger:

    def __init__(self, stdscr):
        self.screen = stdscr

        self.current_sentence = 1
        self.sentence = session.query(model.Sentence).get(1)

        self.current_word = 1
        self.word = session.query(model.Word).get(1)

    def next_word(self):
        if self.current_word + 1 < session.query(model.Word).count():
            self.current_word += 1
            self.word = session.query(model.Word).get(self.current_word)
            self.sentence = self.word.sentence
            self.current_sentence = self.sentence.id

    def prev_word(self):
        if self.current_word > 0:
            self.current_word -= 1
            self.word = session.query(model.Word).get(self.current_word)
            self.sentence = self.word.sentence
            self.current_sentence = self.sentence.id

    def next_sentence(self):
        if self.current_sentence < session.query(model.Sentence).count():
            self.current_sentence += 1
            self.sentence = session.query(model.Sentence).get(
                self.current_sentence)
            self.word = self.sentence.words[0]
            self.current_word = self.word.id

    def prev_sentence(self):
        if self.current_sentence > 0:
            self.current_sentence -= 1
            self.sentence = session.query(model.Sentence).get(
                self.current_sentence)
            self.word = self.sentence.words[-1]
            self.current_word = self.word.id

    def next_character(self):
        self.word = session.query(model.Word).\
                    filter(model.Word.pos == 'NNP').\
                    filter(model.Word.id > self.current_word).first()
        self.current_word = self.word.id
        self.sentence = self.word.sentence
        self.current_sentence = self.sentence.id
        # TODO: ignore registered characters

    def render_sentences(self):
        s = session.query(model.Sentence).get(self.current_sentence)

        s.set_word_coords()
        for w in s.words:

            if w is self.word:
                color = curses.color_pair(3)
            else:
                color = curses.color_pair(2)

            self.screen.addstr(w.y, w.x,
                               w.word,
                               color)

    def render_pos(self):
        pos = "sentence %s of %s (%0.2d%%) [word %s of %s]" \
              % \
              (self.current_sentence,

               session.query(model.Sentence).count(),

               (self.current_sentence * 100.0) /
               session.query(model.Sentence).count(),

               self.current_word + 1,

               session.query(model.Word).count()
               )

        # print sentence number
        self.screen.addstr(0, 0,
                           pos,
                           curses.color_pair(1))

    def render(self):
        self.render_sentences()
        self.render_pos()
        self.screen.refresh()


def main(stdscr):
    # initialize curses environment
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
    # stdscr.nodelay(1)

    t = Tagger(stdscr)

    while True:

        t.render()

        c = stdscr.getch()

        if c == ord('c') or c == ord('C'):
            if t.current_sentence < session.query(model.Sentence).count():
                t.screen.clear()
                t.next_character()

        elif c == ord('n'):
            t.next_word()
            t.screen.clear()

        elif c == ord('p'):
            t.prev_word()
            t.screen.clear()

        elif c == ord('N'):
            t.next_sentence()
            t.screen.clear()

        elif c == ord('P'):
            t.prev_sentence()
            t.screen.clear()

        elif c == curses.KEY_HOME:
            t.current_sentence = 1
            t.sentence = session.query(model.Sentence).get(1)

            t.current_word = 1
            t.word = session.query(model.Word).get(1)
            t.screen.clear()

        elif c == ord('q'):
            break  # Exit the while()


curses.wrapper(main)
