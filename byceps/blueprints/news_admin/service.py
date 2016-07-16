# -*- coding: utf-8 -*-

"""
byceps.blueprints.news_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..brand.models import Brand
from ..news.models import Item


def get_item_counts_by_brand_id():
    """Return news item counts (including 0) per brand, indexed by brand ID."""
    return dict(db.session \
        .query(
            Brand.id,
            db.func.count(Item.brand_id)
        ) \
        .outerjoin(Item) \
        .group_by(Brand.id) \
        .all())


def count_items_for_brand(brand):
    """Return the number of news items for that brand."""
    return Item.query.for_brand(brand).count()
