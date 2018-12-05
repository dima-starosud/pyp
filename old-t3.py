import curses
import itertools
import operator
from collections import namedtuple
from functools import partial
from types import MappingProxyType
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


VALID_CELLS = 0b111_111_111

WIN_COMBINATIONS = (
    0b111_000_000,
    0b000_111_000,
    0b000_000_111,

    0b100_100_100,
    0b010_010_010,
    0b001_001_001,

    0b100_010_001,
    0b001_010_100,
)

X = 'X'
O = 'O'

NEXT_PLAYER_TURN = MappingProxyType({
    X: O,
    O: X,
})

T3 = namedtuple('T3', 'active_player, active_cell, player_x, player_o')
T3.P_MAP = MappingProxyType({X: 'player_x', O: 'player_o'})
T3.active_player_attr = property(lambda me: me.P_MAP[me.active_player])
T3.active_player_state = property(lambda me: getattr(me, me.active_player_attr))
T3.occupied_cells = property(lambda me: me.player_x | me.player_o)
T3.full = property(lambda me: VALID_CELLS == me.occupied_cells)


def empty_t3():
    return T3(active_player=X, active_cell=0, player_x=0, player_o=0)


def finish_turn(t3: T3) -> T3:
    assert t3.active_cell
    t3 = t3._replace(
        active_player=NEXT_PLAYER_TURN[t3.active_player],
        active_cell=0,
        **{t3.active_player_attr: t3.active_player_state | t3.active_cell},
    )

    if not t3.full:
        t3 = activate_cell(t3)
    return t3


def activate_cell(t3: T3) -> T3:
    assert not t3.active_cell
    assert not t3.full
    return normalize_active_cell(t3._replace(active_cell=0b100_000_000))


def lshift(a, b):
    return operator.lshift(a, b)


def rshift(a, b):
    return operator.rshift(a, b)


DIR_HANDLERS = MappingProxyType({
    curses.KEY_LEFT: (partial(lshift, b=1), 1),
    curses.KEY_RIGHT: (partial(rshift, b=1), 0b100_000_000),
    curses.KEY_UP: (partial(lshift, b=3), 1),
    curses.KEY_DOWN: (partial(rshift, b=3), 0b100_000_000),
})


def move_active_cell(t3: T3, direction) -> T3:
    assert t3.active_cell
    assert not t3.full
    handler, default = DIR_HANDLERS[direction]
    return normalize_active_cell(t3._replace(
        active_cell=handler(t3.active_cell) & VALID_CELLS or default
    ))


def normalize_active_cell(t3: T3) -> T3:
    assert t3.active_cell
    assert not t3.full
    active_cell = t3.active_cell
    while True:
        if t3.occupied_cells | active_cell != t3.occupied_cells:
            break
        active_cell = (active_cell << 1) & VALID_CELLS or 1
    return t3._replace(active_cell=active_cell)


KEY_SPACE = 32

T3_GAME_ACTIONS = MappingProxyType({
    KEY_SPACE: finish_turn,
    curses.KEY_LEFT: partial(move_active_cell, direction=curses.KEY_LEFT),
    curses.KEY_RIGHT: partial(move_active_cell, direction=curses.KEY_RIGHT),
    curses.KEY_UP: partial(move_active_cell, direction=curses.KEY_UP),
    curses.KEY_DOWN: partial(move_active_cell, direction=curses.KEY_DOWN),
})


def start_over_again(*_):
    return activate_cell(empty_t3())


T3_GAME_OVER_ACTIONS = MappingProxyType({
    KEY_SPACE: start_over_again,
})


def t3_actions(t3: T3):
    gs = game_state(t3)
    if 'turn' in gs:
        return T3_GAME_ACTIONS
    return T3_GAME_OVER_ACTIONS


def render_bin(x: int, value: str) -> str:
    assert 0 <= x <= VALID_CELLS
    return '{:9b}'.format(x).replace('0', ' ').replace('1', value)


def merge_strings(*strings):
    s = ''
    for cs in zip(*strings):
        c, = (set(cs) - {' '}) or {' '}
        s += c
    return s


TEMPLATE = """{}
┏━┳━┳━┓
┃{}┃{}┃{}┃
┣━╋━╋━┫
┃{}┃{}┃{}┃
┣━╋━╋━┫
┃{}┃{}┃{}┃
┗━┻━┻━┛
"""

_TURN = 'player {} turn'

X_TURN = _TURN.format(X)
O_TURN = _TURN.format(O)
X_WON = 'player X won'
O_WON = 'player O won'
DRAW = 'draw'


def game_state(t3: T3) -> str:
    x_won = t3.player_x in WIN_COMBINATIONS
    o_won = t3.player_o in WIN_COMBINATIONS
    assert not (x_won and o_won)
    if x_won:
        return X_WON
    if o_won:
        return O_WON
    draw = (all(t3.player_x & wc for wc in WIN_COMBINATIONS) and
            all(t3.player_o & wc for wc in WIN_COMBINATIONS))
    if draw:
        return DRAW
    return _TURN.format(t3.active_player)


def render_message(t3: T3):
    return game_state(t3)


def render_t3(t3: T3) -> str:
    string = merge_strings(
        render_bin(t3.active_cell, t3.active_player.lower()),
        render_bin(t3.player_x, X),
        render_bin(t3.player_o, O),
    )
    return TEMPLATE.format(render_message(t3), *string)


def t3_game(key_presses: Iterable[int]) -> Iterable[T3]:
    t3 = start_over_again()
    yield t3
    for k in key_presses:
        action = t3_actions(t3).get(k)
        if not action:
            continue
        t3 = action(t3)
        yield t3


if __name__ == '__main__':
    curses_interaction(lambda x: map(render_t3, t3_game(x)))
