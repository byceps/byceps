# -*- coding: utf-8 -*-

"""
byceps.util.navigation
~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from collections import namedtuple


NavigationItem = namedtuple('NavigationItem', ['endpoint', 'label', 'id'])


class Navigation(object):
    """A navigation list.

    The order of items is the order in which they are added.
    """

    def __init__(self):
        self.items = []

    def add_item(self, endpoint, label, *, id=None):
        """Add an item to the navigation."""
        self.items.append(NavigationItem(
            endpoint=endpoint,
            label=label,
            id=id
            ))

    def get_items(self):
        return list(self.items)
