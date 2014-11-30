# -*- coding: utf-8 -*-

from datetime import datetime

from byceps.blueprints.party.models import Party

from .brand import create_brand


def create_party(*, id='acme-2014', brand=None, title='Acme Entertainment Convention 2014'):
    if brand is None:
        brand = create_brand()

    return Party(
        id=id,
        brand=brand,
        title=title,
        starts_at=datetime(2014, 10, 24, 16, 0),
        ends_at=datetime(2014, 10, 26, 13, 0))
