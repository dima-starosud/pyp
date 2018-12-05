import curses
import itertools
from typing import Callable, Iterable


def curses_interaction(transformer: Callable[[Iterable[int]], Iterable[str]],
                       timeout_ms=100):
    window = curses.initscr()
    try:
        curses.noecho()
        curses.cbreak()
        window.keypad(1)

        key_presses = itertools.starmap(window.getch, itertools.repeat(()))
        strings = transformer(key_presses)

        for s in strings:
            window.erase()
            window.addstr(s)
            window.refresh()
            curses.napms(timeout_ms)
    finally:
        curses.endwin()
