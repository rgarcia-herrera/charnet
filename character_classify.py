import curses

class Tagger:

    def __init__(self, stdscr, text):
        self.text = text
        self.stdscr = stdscr

    def curses_render(self, t):
        color = curses.color_pair(1)
        color = curses.color_pair(2)
        self.stdscr.addstr(2, 4, self.text, color)
        self.stdscr.refresh()


def main(stdscr):
    # initialize curses environment
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    stdscr.nodelay(1)


    t = Tagger(stdscr, 
               "aguas con el perro")

    while True:
        t.curses_render(t) 
        c = stdscr.getch()
        if c == ord('p'):
            t.text = 'pito'
        elif c == ord('q'):
            break  # Exit the while()
        elif c == curses.KEY_HOME:
            x = y = 0        



curses.wrapper(main)

