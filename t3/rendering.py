from functools import singledispatch
from types import MappingProxyType as Map

from t3.data import Board, GameOver, NextTurn, Position

TEMPLATE = """Tic-Tac-Toe
┏━┳━┳━┓
┃{}┃{}┃{}┃
┣━╋━╋━┫
┃{}┃{}┃{}┃
┣━╋━╋━┫
┃{}┃{}┃{}┃
┗━┻━┻━┛
{}"""

EMPTY_BOARD = Map({p: ' ' for p in Position.sorted_members()})


@singledispatch
def render(x):
    raise TypeError('Cannot render {}'.format(type(x)))


def board_values(board: Board):
    return {k: v.value for k, v in board.items()}


@render.register
def render_next_turn(game: NextTurn):
    board = {**EMPTY_BOARD, **board_values(game.board), game.position: game.player.value.lower()}
    return TEMPLATE.format(*(board[p] for p in Position.sorted_members()), game)


@render.register
def render_game_over(game: GameOver):
    board = {**EMPTY_BOARD, **board_values(game.board)}
    return TEMPLATE.format(*(board[p] for p in Position.sorted_members()), game)
