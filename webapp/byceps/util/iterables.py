# -*- coding: utf-8 -*-

"""
byceps.util.iterables
~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from itertools import islice


def find(iterable, predicate):
    """Return the first element in the iterable that matches the
    predicate.

    If none does, return ``None``.
    """
    for elem in iterable:
        if predicate(elem):
            return elem
