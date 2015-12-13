# -*- coding: utf-8 -*-

"""
byceps.blueprints.board_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..brand.models import Brand
from ..board.models.category import Category


def get_brands_with_category_counts():
    """Yield (brand, category count) pairs."""
    brands = Brand.query.all()

    category_counts_by_brand_id = _get_category_counts_by_brand_id()

    for brand in brands:
        category_count = category_counts_by_brand_id.get(brand.id, 0)
        yield brand, category_count


def _get_category_counts_by_brand_id():
    return dict(db.session \
        .query(
            Category.brand_id,
            db.func.count(Category.brand_id)
        ) \
        .group_by(Category.brand_id) \
        .all())
