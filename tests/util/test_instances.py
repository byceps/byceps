# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest import TestCase

from byceps.util.instances import ReprBuilder


class ReprBuilderTestCase(TestCase):

    def setUp(self):
        self.instance = Instance()

    def test_without_any_values(self):
        actual = ReprBuilder(self.instance) \
            .build()

        assert actual == '<Instance()>'

    def test_with_looked_up_values(self):
        actual = ReprBuilder(self.instance) \
            .add_with_lookup('first_name') \
            .add_with_lookup('last_name') \
            .add_with_lookup('age') \
            .add_with_lookup('delivers_pizza') \
            .build()

        assert actual == \
            '<Instance(first_name=Hiro, last_name=Protagonist, age=26, delivers_pizza=True)>'

    def test_with_given_value(self):
        actual = ReprBuilder(self.instance) \
            .add_with_lookup('last_name') \
            .add('last_name length', 11) \
            .build()

        assert actual == \
            '<Instance(last_name=Protagonist, last_name length=11)>'

    def test_with_custom_value(self):
        actual = ReprBuilder(self.instance) \
            .add('last_name', 'Protagonist') \
            .add_custom('is of full age') \
            .build()

        assert actual == \
            '<Instance(last_name=Protagonist, is of full age)>'


class Instance(object):

    def __init__(self):
        self.first_name = 'Hiro'
        self.last_name = 'Protagonist'
        self.age = 26
        self.delivers_pizza = True
