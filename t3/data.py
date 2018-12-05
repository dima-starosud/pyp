from dataclasses import dataclass, replace
from enum import Enum
from operator import attrgetter, methodcaller
from types import MappingProxyType as Map
from typing import Mapping

from t3.iterators import drop, iterate


class Player(Enum):
    X = 'X'
    O = 'O'

    def other(self):
        o, = set(type(self).__members__.values()) - {self}
        return o


class Enter(Enum):
    ENTER = 0


class Move(Enum):
    LEFT = -1
    RIGHT = +1
    UP = -3
    DOWN = +3


POSITION_SUP = 9


class PositionBase(Enum):
    def move(self, move: Move):
        return type(self)((self.value + move.value) % POSITION_SUP)

    @classmethod
    def sorted_members(cls):
        return tuple(sorted(cls.__members__.values(), key=attrgetter('value')))


Position = PositionBase('Position', {'P{}'.format(i): i for i in range(POSITION_SUP)})

# TODO should be separate class
Board = Mapping[Position, Player]


def empty_cells(board: Board):
    return frozenset(Position.__members__.values()) - board.keys()


@dataclass(frozen=True)
class NextTurn:
    board: Board
    player: Player
    position: Position

    def __post_init__(self):
        assert self.position not in self.board

    def move(self, move: Move):
        next_positions = iterate(self.position, methodcaller('move', move))
        next_positions = drop(next_positions, 1)
        next_position = next(filter(empty_cells(self.board).__contains__, next_positions))
        return replace(self, position=next_position)

    def apply(self):
        next_board = Map({**self.board, self.position: self.player})
        empty_cells_ = empty_cells(next_board)
        if not empty_cells_:
            return GameOver(next_board)
        return replace(self,
                       board=next_board,
                       player=self.player.other(),
                       position=min(empty_cells_, key=attrgetter('value')))


@dataclass(frozen=True)
class GameOver:
    board: Board
