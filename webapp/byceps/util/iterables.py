# -*- coding: utf-8 -*-

"""
byceps.util.iterables
~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from itertools import islice, tee


def find(iterable, predicate):
    """Return the first element in the iterable that matches the
    predicate.

    If none does, return ``None``.
    """
    for elem in iterable:
        if predicate(elem):
            return elem


def index_of(iterable, predicate):
    """Return the (0-based) index of the first element in the iterable
    that matches the predicate.

    If none does, return ``None``.
    """
    for i, elem in enumerate(iterable):
        if predicate(elem):
            return i


def pairwise(iterable):
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
