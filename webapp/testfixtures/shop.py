# -*- coding: utf-8 -*-

"""
testfixtures.shop
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from decimal import Decimal

from byceps.blueprints.shop.models.article import Article
from byceps.blueprints.shop.models.order import Order
from byceps.blueprints.shop.models.sequence import PartySequence

from .party import create_party


def create_article(*, party=None, serial_number=1, description='Cool thing',
                   price=None, tax_rate=None, available_from=None,
                   available_until=None, quantity=1):
    if party is None:
        party = create_party()

    item_number = '{}-{:02d}-A{:05d}'.format(
        party.brand.code, party.number, serial_number)

    if price is None:
        price = Decimal('24.95')

    if tax_rate is None:
        tax_rate = Decimal('0.19')

    return Article(
        party=party,
        item_number=item_number,
        description=description,
        price=price,
        tax_rate=tax_rate,
        available_from=available_from,
        available_until=available_until,
        quantity=quantity)


def create_order(placed_by, *, party=None, serial_number=1):
    if party is None:
        party = create_party()

    order_number = '{}-{:02d}-B{:05d}'.format(
        party.brand.code, party.number, serial_number)

    return Order(
        party=party,
        order_number=order_number,
        placed_by=placed_by,
        first_names=placed_by.detail.first_names,
        last_name=placed_by.detail.last_name,
        date_of_birth=placed_by.detail.date_of_birth,
        country=placed_by.detail.country,
        zip_code=placed_by.detail.zip_code,
        city=placed_by.detail.city,
        street=placed_by.detail.street,
    )


def create_party_sequence(party, purpose, *, value=0):
    sequence = PartySequence(party, purpose)
    sequence.value = value
    return sequence
