"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.instances import ReprBuilder


def test_without_any_values():
    instance = Instance()

    actual = ReprBuilder(instance).build()

    assert actual == '<Instance()>'


def test_with_looked_up_values():
    instance = Instance()

    actual = ReprBuilder(instance) \
        .add_with_lookup('first_name') \
        .add_with_lookup('last_name') \
        .add_with_lookup('age') \
        .add_with_lookup('delivers_pizza') \
        .add_with_lookup('favorite_customer') \
        .build()

    assert actual == "<Instance(first_name='Hiro', last_name='Protagonist', age=26, delivers_pizza=True, favorite_customer=None)>"


def test_with_given_value():
    instance = Instance()

    actual = ReprBuilder(instance) \
        .add_with_lookup('last_name') \
        .add('last_name length', 11) \
        .build()

    assert actual == "<Instance(last_name='Protagonist', last_name length=11)>"


def test_with_custom_value():
    instance = Instance()

    actual = ReprBuilder(instance) \
        .add('last_name', 'Protagonist') \
        .add_custom('is of full age') \
        .build()

    assert actual == "<Instance(last_name='Protagonist', is of full age)>"


class Instance:

    def __init__(self):
        self.first_name = 'Hiro'
        self.last_name = 'Protagonist'
        self.age = 26
        self.delivers_pizza = True
        self.favorite_customer = None
