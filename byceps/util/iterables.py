"""
byceps.util.iterables
~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from itertools import tee
from typing import Callable, Iterable, Iterator, Optional, Tuple, TypeVar


T = TypeVar('T')

Predicate = Callable[[T], bool]


def find(iterable: Iterable[T], predicate: Predicate) -> Optional[T]:
    """Return the first element in the iterable that matches the
    predicate.

    If none does, return ``None``.
    """
    for elem in iterable:
        if predicate(elem):
            return elem

    return None


def index_of(predicate: Predicate, iterable: Iterable[T]) -> Optional[int]:
    """Return the (0-based) index of the first element in the iterable
    that matches the predicate.

    If none does, return ``None``.
    """
    for i, elem in enumerate(iterable):
        if predicate(elem):
            return i

    return None


def pairwise(iterable: Iterable[T]) -> Iterator[Tuple[T, T]]:
    """Return each element paired with its next one.

    Example:
        xs -> (x0, x1), (x1, x2), (x2, x3), ...

    As seen in the Python standard library documentation of the
    `itertools` module:
    https://docs.python.org/3/library/itertools.html#itertools-recipes
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
