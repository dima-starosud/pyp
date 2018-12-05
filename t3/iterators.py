import itertools
import operator
from functools import partial
from typing import Callable, Iterable, Iterator, Optional, TypeVar

X = TypeVar('X')
Y = TypeVar('Y')
T = TypeVar('T')


def scan_optional(xs: Iterable[X], y: Y, f: Callable[[Y, X], Optional[Y]]) -> Iterator[Y]:
    yield y
    for x in xs:
        for y in optional(f(y, x)):
            yield y


def optional(x: Optional[T], predicate=partial(operator.is_not, None)) -> Iterator[T]:
    if predicate(x):
        yield x


def iterate(x: X, f: Callable[[X], X]) -> Iterator[X]:
    while True:
        yield x
        x = f(x)


def take(xs: Iterable[X], n: int) -> Iterator[X]:
    return itertools.islice(xs, n)


def drop(xs: Iterable[X], n: int) -> Iterator[X]:
    return itertools.islice(xs, n, None)
