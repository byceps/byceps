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
