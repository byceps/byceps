# -*- coding: utf-8 -*-

"""
byceps.blueprints.news.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from . models import CurrentVersionAssociation, Item, ItemVersion


def create_item(brand, slug, creator, title, body, *, image_url_path=None):
    """Create a news item, a version, and set the version as the item's
    current one.
    """
    item = Item(brand, slug)
    db.session.add(item)

    version = _create_version(item, creator, title, body,
                              image_url_path=image_url_path)
    db.session.add(version)

    current_version_association = CurrentVersionAssociation(item, version)
    db.session.add(current_version_association)

    db.session.commit()

    return item


def update_item(item, creator, title, body, *, image_url_path=None):
    """Update a news item by creating a new version of it and setting
    the new version as the current one.
    """
    version = _create_version(item, creator, title, body,
                              image_url_path=image_url_path)
    db.session.add(version)

    item.current_version = version

    db.session.commit()


def _create_version(item, creator, title, body, *, image_url_path=None):
    version = ItemVersion(item, creator, title, body)
    if image_url_path:
        version.image_url_path = image_url_path
    return version


def find_item_by_id(item_id):
    """Return the item with that id, or `None` if not found."""
    return Item.query.get(item_id)


def get_items_paginated(brand_id, page, items_per_page):
    """Return the news items to show on the specified page."""
    return Item.query \
        .for_brand_id(brand_id) \
        .with_current_version() \
        .order_by(Item.published_at.desc()) \
        .paginate(page, items_per_page)


def get_item(brand_id, slug):
    """Return the news item identified by that slug."""
    return Item.query \
        .for_brand_id(brand_id) \
        .with_current_version() \
        .filter_by(slug=slug) \
        .first_or_404()
