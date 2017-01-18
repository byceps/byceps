# -*- coding: utf-8 -*-

"""
byceps.services.brand.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models import Brand


def create_brand(brand_id, title):
    """Create a brand."""
    brand = Brand(brand_id, title)

    db.session.add(brand)
    db.session.commit()

    return brand


def find_brand(brand_id):
    """Return the brand with that id, or `None` if not found."""
    return Brand.query.get(brand_id)


def get_brands():
    """Return all brands, ordered by title."""
    return Brand.query \
        .order_by(Brand.title) \
        .all()


def count_brands():
    """Return the number of brands."""
    return Brand.query.count()
