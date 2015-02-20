# -*- coding: utf-8 -*-

"""
byceps.blueprints.news.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from . models import Item


def get_items_paginated(brand, page, items_per_page):
    """Return the news items to show on the specified page."""
    return Item.query \
        .for_brand(brand) \
        .order_by(Item.published_at.desc()) \
        .paginate(page, items_per_page)


def get_item(brand, slug):
    """Return the news item identified by that slug."""
    return Item.query \
        .for_brand(brand) \
        .filter_by(slug=slug) \
        .first_or_404()
