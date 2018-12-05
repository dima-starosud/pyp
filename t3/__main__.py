import curses
from types import MappingProxyType

from t3.actions import Action, NEW_GAME, handle_action
from t3.engine import curses_interaction
from t3.iterators import scan_optional
from t3.rendering import render

KEY_ACTION = MappingProxyType({
    curses.KEY_LEFT: Action.LEFT,
    curses.KEY_RIGHT: Action.RIGHT,
    curses.KEY_UP: Action.UP,
    curses.KEY_DOWN: Action.DOWN,
    32: Action.ENTER,
})


def game(keys):
    keys = filter(None, map(KEY_ACTION.get, keys))
    states = scan_optional(keys, NEW_GAME, handle_action)
    return map(render, states)


curses_interaction(game)
