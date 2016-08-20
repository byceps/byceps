# -*- coding: utf-8 -*-

"""
byceps.blueprints.brand.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from .models import Brand


def count_brands():
    """Return the number of brands."""
    return Brand.query.count()


def find_brand(brand_id):
    """Return the brand with that id, or `None` if not found."""
    return Brand.query.get(brand_id)


def get_brands():
    """Return all brands, ordered by title."""
    return Brand.query \
        .order_by(Brand.title) \
        .all()
