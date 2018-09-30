"""
byceps.database
~~~~~~~~~~~~~~~

Database utilities.

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Callable, TypeVar
import uuid

from flask_sqlalchemy import BaseQuery, Pagination, SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Query


F = TypeVar('F')
T = TypeVar('T')

Mapper = Callable[[F], T]


db = SQLAlchemy(session_options={'autoflush': False})


db.JSONB = JSONB


class Uuid(UUID):

    def __init__(self):
        super().__init__(as_uuid=True)


db.Uuid = Uuid


def generate_uuid() -> uuid.UUID:
    """Generate a random UUID (Universally Unique IDentifier)."""
    return uuid.uuid4()


def paginate(query: Query, page: int, per_page: int,
             *, item_mapper: Mapper=None) -> Pagination:
    """Return `per_page` items from page `page`."""
    if page < 1:
        page = 1

    if per_page < 1:
        raise ValueError('The number of items per page must be positive.')

    offset = (page - 1) * per_page

    items = query \
        .limit(per_page) \
        .offset(offset) \
        .all()

    item_count = len(items)
    if page == 1 and item_count < per_page:
        total = item_count
    else:
        total = query.order_by(None).count()

    if item_mapper is not None:
        items = [item_mapper(item) for item in items]

    # Intentionally pass no query object.
    return Pagination(None, page, per_page, total, items)
