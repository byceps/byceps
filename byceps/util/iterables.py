"""
byceps.util.iterables
~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from itertools import tee
from typing import Any, Callable, Iterable, Iterator, Tuple


Predicate = Callable[[Any], bool]


def find(predicate: Predicate, iterable: Iterable[Any]) -> Any:
    """Return the first element in the iterable that matches the
    predicate.

    If none does, return ``None``.
    """
    for elem in iterable:
        if predicate(elem):
            return elem


def index_of(predicate: Predicate, iterable: Iterable[Any]) -> int:
    """Return the (0-based) index of the first element in the iterable
    that matches the predicate.

    If none does, return ``None``.
    """
    for i, elem in enumerate(iterable):
        if predicate(elem):
            return i


def pairwise(iterable: Iterable[Any]) -> Iterator[Tuple[Any, Any]]:
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
