# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest import TestCase

from byceps.blueprints.shop.models.cart import CartItem

from testfixtures.shop import create_article


class CartItemCreationTestCase(TestCase):

    def test_init_with_positive_quantity(self):
        quantity = 1
        item = self.create_item(quantity)
        self.assertEqual(item.quantity, quantity)

    def test_init_with_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.create_item(0)

    def test_init_with_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.create_item(-1)

    # helpers

    def create_item(self, quantity):
        article = create_article()
        return CartItem(article, quantity)
