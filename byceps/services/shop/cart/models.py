"""
byceps.services.shop.cart.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....util.instances import ReprBuilder


class Cart(object):
    """A shopping cart."""

    def __init__(self):
        self._items = []

    def add_item(self, article, quantity):
        item = CartItem(article, quantity)
        self._items.append(item)

    def get_items(self):
        return self._items

    def is_empty(self):
        return not self._items

    def __repr__(self):
        return ReprBuilder(self) \
            .add_custom('{:d} items'.format(len(self._items))) \
            .build()


class CartItem(object):
    """An article with a quantity."""

    def __init__(self, article, quantity):
        if quantity < 1:
            raise ValueError('Quantity must be a positive number.')

        self.article = article
        self.quantity = quantity

    def __repr__(self):
        return ReprBuilder(self) \
            .add('article', self.article.item_number) \
            .add_with_lookup('quantity') \
            .build()
