import curses
import argparse
from pattern.en import parsetree
from time import sleep

parser = argparse.ArgumentParser(
    description='Create character networks from plaintext.')
parser.add_argument('--text',
                    type=argparse.FileType('r'), required=True,
                    help='a plain text file')
parser.add_argument('--distance',
                    default=120,
                    help='word distance to connect characters')
args = parser.parse_args()


class Tagger:

    def __init__(self, stdscr, text):
        self.text = text
        self.screen = stdscr
        self.tree = parsetree(text)
        self.current_sentence = 0

    def get_sentence(self):
        return self.tree[self.current_sentence].string

    def next_character(self):
        self.current_sentence += 1
        while 'NNP' not in \
              list(self.tree[self.current_sentence].parts_of_speech) \
              and self.current_sentence < len(self.tree.sentences):
            self.current_sentence += 1

    def get_pos(self):
        return "sentence %s, of %s (%0.2d%%)" % (self.current_sentence,
                                                 len(self.tree.sentences),
                                                 (self.current_sentence * 100.0)
                                                 / len(self.tree.sentences))

    def render_sentence(self):
        sentence = self.get_sentence()
        # show sentence
        self.screen.addstr(3, 0,
                           sentence,
                           curses.color_pair(2))
        # color characters
        for c in self.tree[self.current_sentence].nouns:
            if c.pos == 'NNP':
                x = sentence.index(c.string)
                self.screen.addstr(3, x,
                                   c.string,
                                   curses.color_pair(3))

    def render_pos(self):
        # print sentence number
        self.screen.addstr(0, 0,
                           self.get_pos(),
                           curses.color_pair(1))

    def render(self):
        self.render_sentence()
        self.render_pos()
        self.screen.refresh()


def main(stdscr):
    # initialize curses environment
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)
    stdscr.nodelay(1)

    t = Tagger(stdscr,
               args.text.read())

    while True:

        t.render()

        c = stdscr.getch()
        if c == ord('P'):
            if t.current_sentence > 0:
                t.screen.clear()
                t.current_sentence -= 1

        elif c == ord('N'):
            if t.current_sentence < len(t.tree.sentences):
                t.screen.clear()
                t.current_sentence += 1

        elif c == ord('c') or c == ord('C'):
            if t.current_sentence < len(t.tree.sentences):
                t.screen.clear()
                t.next_character()

        elif c == curses.KEY_HOME:
            t.current_sentence = 0

        elif c == ord('q'):
            break  # Exit the while()

        sleep(0.33)

curses.wrapper(main)
