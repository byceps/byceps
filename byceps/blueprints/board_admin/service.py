# -*- coding: utf-8 -*-

"""
byceps.blueprints.board_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..board.models.category import Category
from ..board.models.posting import Posting
from ..board.models.topic import Topic


def count_categories_for_brand(brand):
    """Return the number of categories for that brand."""
    return Category.query.for_brand(brand).count()


def count_topics_for_brand(brand):
    """Return the number of topics for that brand."""
    return Topic.query \
        .join(Category).filter(Category.brand_id == brand.id) \
        .count()


def count_postings_for_brand(brand):
    """Return the number of postings for that brand."""
    return Posting.query \
        .join(Topic).join(Category).filter(Category.brand_id == brand.id) \
        .count()


def get_categories(brand):
    """Return all categories for that brand, ordered by position."""
    return Category.query \
        .for_brand(brand) \
        .order_by(Category.position) \
        .all()


def create_category(brand, slug, title, description):
    """Create a category in that brand's board."""
    category = Category(brand, slug, title, description)
    brand.board_categories.append(category)

    db.session.commit()

    return category


def update_category(category, slug, title, description):
    """Update the category."""
    category.slug = slug.strip().lower()
    category.title = title.strip()
    category.description = description.strip()

    db.session.commit()

    return category


def move_category_up(category):
    """Move a category upwards by one position."""
    category_list = category.brand.board_categories

    if category.position == 1:
        raise ValueError('Category already is at the top.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position - 2, popped_category)

    db.session.commit()


def move_category_down(category):
    """Move a category downwards by one position."""
    category_list = category.brand.board_categories

    if category.position == len(category_list):
        raise ValueError('Category already is at the bottom.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position, popped_category)

    db.session.commit()
