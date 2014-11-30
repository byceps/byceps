# -*- coding: utf-8 -*-

from datetime import date

from byceps.blueprints.shop.models import Article, Order
from byceps.util.money import EuroAmount

from .party import create_party


def create_article(*, party=None, description='Cool thing',
                   available_from=None, available_until=None, price=None,
                   quantity=1):
    if party is None:
        party = create_party()

    if price is None:
        price = EuroAmount(24, 95)

    return Article(
        party=party,
        description=description,
        price=price,
        available_from=available_from,
        available_until=available_until,
        quantity=quantity)


def create_order(placed_by, *, party=None):
    if party is None:
        party = create_party()

    return Order(
        party=party,
        placed_by=placed_by,
        first_names='John Joseph',
        last_name='Doe',
        date_of_birth=date(1993, 2, 15),
        zip_code='31337',
        street='Elite Street 1337',
        city='Atrocity',
    )
