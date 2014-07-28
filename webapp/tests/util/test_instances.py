# -*- coding: utf-8 -*-

from unittest import TestCase

from byceps.util.instances import ReprBuilder


class ReprBuilderTestCase(TestCase):

    def setUp(self):
        self.instance = Instance()

    def test_without_attributes(self):
        actual = ReprBuilder(self.instance) \
            .build()

        self.assertEqual(actual, '<Instance()>')

    def test_with_attributes(self):
        actual = ReprBuilder(self.instance) \
            .add('first_name') \
            .add('last_name') \
            .add('age') \
            .add('delivers_pizza') \
            .build()

        self.assertEqual(
            actual,
            '<Instance(first_name=Hiro, last_name=Protagonist, age=26, delivers_pizza=True)>')


class Instance(object):

    def __init__(self):
        self.first_name = 'Hiro'
        self.last_name = 'Protagonist'
        self.age = 26
        self.delivers_pizza = True
