from operator import methodcaller
from types import MappingProxyType as Map
from typing import Optional, Union

from t3.data import Enter, GameOver, Move, NextTurn, Player, Position


class Action:
    ENTER = Enter.ENTER
    LEFT = Move.LEFT
    RIGHT = Move.RIGHT
    UP = Move.UP
    DOWN = Move.DOWN


NEW_GAME = NextTurn(Map({}), Player.X, Position.P0)

ACTIONS = Map({
    NextTurn: Map({
        **{move: methodcaller('move', move=move) for move in Move.__members__.values()},
        Action.ENTER: methodcaller('apply'),
    }),

    GameOver: Map({
        Action.ENTER: lambda _: NEW_GAME,
    }),
})

Game = Union[NextTurn, GameOver]


def handle_action(game: Game, action: Action) -> Optional[Game]:
    handler = ACTIONS[type(game)].get(action)
    if handler is None:
        return None
    return handler(game)
