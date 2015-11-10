# -*- coding: utf-8 -*-

"""
byceps.blueprints.news_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..brand.models import Brand
from ..news.models import Item


def get_brands_with_item_counts():
    """Yield (brand, item count) pairs."""
    brands = Brand.query.all()

    item_counts_by_brand_id = _get_item_counts_by_brand_id()

    for brand in brands:
        item_count = item_counts_by_brand_id.get(brand.id, 0)
        yield brand, item_count


def _get_item_counts_by_brand_id():
    return dict(db.session \
        .query(
            Item.brand_id,
            db.func.count(Item.brand_id)
        ) \
        .group_by(Item.brand_id) \
        .all())
