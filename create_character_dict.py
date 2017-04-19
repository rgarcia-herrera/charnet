import curses
import argparse
from pattern.en import parsetree
from time import sleep
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
parser.add_argument('--text',
                    type=argparse.FileType('r'), required=True,
                    help='a plain text file')
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

model.Base.metadata.create_all(engine)
model.session = session


class Tagger:

    def __init__(self, stdscr, text):
        self.screen = stdscr

        self.tree = parsetree(text)

        self.current_sentence = 0
        self.sentence = self.tree[0]

        self.current_word = 0
        self.word = self.sentence.words[0]

        # display position
        self.pos = 0

    def next_word(self):
        if self.current_word + 1 < len(self.sentence.words):
            self.current_word += 1
            self.word = self.sentence.words[self.current_word]
        elif self.current_word + 1 == len(self.sentence.words):
            self.next_sentence()

    def prev_word(self):
        if self.current_word > 0:
            self.current_word -= 1
            self.word = self.sentence.words[self.current_word]
        else:
            self.prev_sentence()

    def next_sentence(self):
        if self.current_sentence < len(self.tree.sentences):
            self.current_sentence += 1
            self.current_word = 0

        self.sentence = self.tree[self.current_sentence]
        self.word = self.sentence.words[self.current_word]

    def prev_sentence(self):
        if self.current_sentence > 0:
            self.current_sentence -= 1
            self.sentence = self.tree[self.current_sentence]
            self.current_word = len(self.sentence.words) - 1
            self.word = self.sentence.words[self.current_word]

    def next_character(self):
        self.next_sentence()
        while 'NNP' not in \
              list(self.sentence.parts_of_speech):
            self.next_sentence()
            # TODO: shift current word to NNP
            # TODO: ignore previously found characters

    def get_word_pos(self):
        wordchars = 0
        for i in range(0, self.word.index):
            wordchars += len(self.sentence.words[i].string) + 1

#        spaces = self.sentence.string.count(' ', pos, pos)

        return wordchars

    def render_sentences(self):
        # show sentence
        self.screen.addstr(3, 0,
                           self.sentence.string,
                           curses.color_pair(2))

        # color current word
        self.screen.addstr(3, self.get_word_pos(),
                           self.word.string,
                           curses.color_pair(3))

    def render_pos(self):
        pos = "sentence %s, of %s (%0.2d%%) word in sentence: %s of %s" \
              % \
              (self.current_sentence,
               len(self.tree.sentences),
               (self.current_sentence * 100.0) / len(self.tree.sentences),
               self.current_word + 1,
               len(self.sentence.words))

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
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)
    # stdscr.nodelay(1)

    t = Tagger(stdscr,
               args.text.read())

    while True:

        t.render()

        c = stdscr.getch()

        if c == ord('c') or c == ord('C'):
            if t.current_sentence < len(t.tree.sentences):
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
            t.current_sentence = 0

        elif c == ord('q'):
            break  # Exit the while()

#        sleep(0.133)


curses.wrapper(main)
