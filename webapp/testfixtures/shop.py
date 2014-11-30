# -*- coding: utf-8 -*-

from byceps.blueprints.shop.models import Article
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
