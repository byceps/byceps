# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest import TestCase

from byceps.blueprints.shop.models.cart import Cart

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
        article = create_article()
        self.cart.add_item(article, quantity)
