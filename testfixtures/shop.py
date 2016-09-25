# -*- coding: utf-8 -*-

"""
testfixtures.shop
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from decimal import Decimal

from byceps.blueprints.shop.models.article import Article
from byceps.blueprints.shop.models.order import Order, Orderer, OrderItem, \
    PaymentMethod
from byceps.services.shop.sequence.models import PartySequence

from .party import create_party


ANY_ARTICLE_ITEM_NUMBER = 'AEC-05-A00009'
ANY_ORDER_NUMBER = 'AEC-03-B00074'


def create_article(*, party=None, item_number=ANY_ARTICLE_ITEM_NUMBER,
                   description='Cool thing', price=None, tax_rate=None,
                   available_from=None, available_until=None, quantity=1):
    if party is None:
        party = create_party()

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


def create_order(placed_by, *, party=None, order_number=ANY_ORDER_NUMBER,
                 payment_method=PaymentMethod.bank_transfer):
    if party is None:
        party = create_party()

    return Order(
        party.id,
        order_number,
        placed_by,
        placed_by.detail.first_names,
        placed_by.detail.last_name,
        placed_by.detail.date_of_birth,
        placed_by.detail.country,
        placed_by.detail.zip_code,
        placed_by.detail.city,
        placed_by.detail.street,
        payment_method,
    )


def create_order_item(order, article, quantity):
    return OrderItem(order, article, quantity)


def create_party_sequence(party, purpose, prefix, *, value=0):
    sequence = PartySequence(party.id, purpose, prefix)
    sequence.value = value
    return sequence
