# -*- coding: utf-8 -*-

"""
testfixtures.shop
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from decimal import Decimal

from byceps.blueprints.shop.models.article import Article
from byceps.blueprints.shop.models.order import Order, Orderer, PaymentMethod
from byceps.blueprints.shop.models.sequence import PartySequence, \
    PartySequencePrefix

from .party import create_party


def create_article(*, party=None, serial_number=1, description='Cool thing',
                   price=None, tax_rate=None, available_from=None,
                   available_until=None, quantity=1):
    if party is None:
        party = create_party()

    prefix = party.shop_number_prefix
    if prefix is None:
        prefix = create_party_sequence_prefix(party)

    item_number = '{}{:05d}'.format(prefix.article_number, serial_number)

    if price is None:
        price = Decimal('24.95')

    if tax_rate is None:
        tax_rate = Decimal('0.19')

    return Article(party.id, item_number, description, price, tax_rate,
                   quantity, available_from=available_from,
                   available_until=available_until)


def create_orderer(user):
    return Orderer(
        user,
        user.detail.first_names,
        user.detail.last_name,
        user.detail.date_of_birth,
        user.detail.country,
        user.detail.zip_code,
        user.detail.city,
        user.detail.street)


def create_order(placed_by, *, party=None, serial_number=1,
                 payment_method=PaymentMethod.cash):
    if party is None:
        party = create_party()

    prefix = party.shop_number_prefix
    if prefix is None:
        prefix = create_party_sequence_prefix(party)

    order_number = '{}{:05d}'.format(prefix.order_number, serial_number)

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
        payment_method=payment_method,
    )


def create_party_sequence_prefix(party, *, article_number_prefix='AEC-03-A',
                                 order_number_prefix='AEC-03-B'):
    return PartySequencePrefix(party, article_number_prefix, order_number_prefix)


def create_party_sequence(party, purpose, *, value=0):
    sequence = PartySequence(party, purpose)
    sequence.value = value
    return sequence
