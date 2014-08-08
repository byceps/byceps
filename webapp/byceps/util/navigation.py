# -*- coding: utf-8 -*-

"""
byceps.util.navigation
~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from collections import namedtuple

from flask import g


NavigationItem = namedtuple('NavigationItem', [
    'endpoint',
    'label',
    'id',
    'required_permission',
])


class Navigation(object):
    """A navigation list.

    The order of items is the order in which they are added.
    """

    def __init__(self):
        self.items = []

    def add_item(self, endpoint, label, *, id=None, required_permission=None):
        """Add an item to the navigation."""
        self.items.append(NavigationItem(
            endpoint=endpoint,
            label=label,
            id=id,
            required_permission=required_permission
            ))

    def get_items(self):
        def current_user_has_permission(item):
            return g.current_user.has_permission(item.required_permission)

        return list(filter(current_user_has_permission, self.items))
