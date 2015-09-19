# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest import TestCase

from byceps.blueprints.shop.models.cart import Cart, CartItem

from testfixtures.shop import create_article


class CartEmptinessTestCase(TestCase):

    def setUp(self):
        self.cart = Cart()

    def test_is_empty_without_items(self):
        self.assertTrue(self.cart.is_empty())

    def test_is_empty_with_one_item(self):
        self.add_item(1)

        self.assertFalse(self.cart.is_empty())

    def test_is_empty_with_multiple_items(self):
        self.add_item(3)
        self.add_item(1)
        self.add_item(6)

        self.assertFalse(self.cart.is_empty())

    # helpers

    def add_item(self, quantity):
        item = self.create_item(quantity)
        self.cart.add_item(item)

    def create_item(self, quantity):
        article = create_article()
        return CartItem(article, quantity)


class CartItemCreationTestCase(TestCase):

    def test_init_with_positive_quantity(self):
        quantity = 1
        item = self.create_item(quantity)
        self.assertEquals(item.quantity, quantity)

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
