# -*- coding: utf-8 -*-

"""
byceps.blueprints.news.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from . models import Item


def get_items_paginated(page, items_per_page):
    """Return the news items to show on the specified page."""
    return Item.query \
        .order_by(Item.published_at.desc()) \
        .paginate(page, items_per_page)
