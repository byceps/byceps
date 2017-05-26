"""
byceps.services.board.category_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db
from ...typing import BrandID

from ..brand.models import Brand

from .models.category import Category, CategoryID


def create_category(brand: Brand, slug: str, title: str, description: str
                   ) -> Category:
    """Create a category in that brand's board."""
    category = Category(brand.id, slug, title, description)
    brand.board_categories.append(category)

    db.session.commit()

    return category


def update_category(category: Category, slug: str, title: str, description: str
                   ) -> Category:
    """Update the category."""
    category.slug = slug.strip().lower()
    category.title = title.strip()
    category.description = description.strip()

    db.session.commit()

    return category


def move_category_up(category: Category) -> None:
    """Move a category upwards by one position."""
    category_list = category.brand.board_categories

    if category.position == 1:
        raise ValueError('Category already is at the top.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position - 2, popped_category)

    db.session.commit()


def move_category_down(category: Category) -> None:
    """Move a category downwards by one position."""
    category_list = category.brand.board_categories

    if category.position == len(category_list):
        raise ValueError('Category already is at the bottom.')

    popped_category = category_list.pop(category.position - 1)
    category_list.insert(popped_category.position, popped_category)

    db.session.commit()


def count_categories_for_brand(brand_id: BrandID) -> int:
    """Return the number of categories for that brand."""
    return Category.query.for_brand_id(brand_id).count()


def find_category_by_id(category_id: CategoryID) -> Optional[Category]:
    """Return the category with that id, or `None` if not found."""
    return Category.query.get(category_id)


def find_category_by_slug(brand_id: BrandID, slug: str) -> Optional[Category]:
    """Return the category for that brand and slug, or `None` if not found."""
    return Category.query \
        .for_brand_id(brand_id) \
        .filter_by(slug=slug) \
        .first()


def get_categories(brand_id: BrandID) -> Sequence[Category]:
    """Return all categories for that brand, ordered by position."""
    return Category.query \
        .for_brand_id(brand_id) \
        .order_by(Category.position) \
        .all()


def get_categories_excluding(brand_id: BrandID, category_id: CategoryID
                            ) -> Sequence[Category]:
    """Return all categories for that brand except for the specified one."""
    return Category.query \
        .for_brand_id(brand_id) \
        .filter(Category.id != category_id) \
        .order_by(Category.position) \
        .all()


def get_categories_with_last_updates(brand_id: BrandID) -> Sequence[Category]:
    """Return the categories for that brand.

    Include the creator of the last posting in each category.
    """
    return Category.query \
        .for_brand_id(brand_id) \
        .options(
            db.joinedload(Category.last_posting_updated_by),
        ) \
        .all()
