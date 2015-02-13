# -*- coding: utf-8 -*-

from datetime import date
from decimal import Decimal

from byceps.blueprints.shop.models import Article, Order, PartySequence
from byceps.util.money import EuroAmount

from .party import create_party


def create_article(*, party=None, description='Cool thing', price=None,
                   tax_rate=None, available_from=None, available_until=None,
                   quantity=1):
    if party is None:
        party = create_party()

    if price is None:
        price = EuroAmount(24, 95)

    if tax_rate is None:
        tax_rate = Decimal('0.19')

    return Article(
        party=party,
        item_number='AEC-03-A00015',
        description=description,
        price=price,
        tax_rate=tax_rate,
        available_from=available_from,
        available_until=available_until,
        quantity=quantity)


def create_order(placed_by, *, party=None):
    if party is None:
        party = create_party()

    return Order(
        party=party,
        order_number='AEC-04-B00376',
        placed_by=placed_by,
        first_names='John Joseph',
        last_name='Doe',
        date_of_birth=date(1993, 2, 15),
        zip_code='31337',
        street='Elite Street 1337',
        city='Atrocity',
    )


def create_party_sequence(party, purpose, *, value=0):
    sequence = PartySequence(party, purpose)
    sequence.value = value
    return sequence
