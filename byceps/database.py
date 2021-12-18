"""
byceps.database
~~~~~~~~~~~~~~~

Database utilities.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Any, Callable, Iterable, Optional, TypeVar
import uuid

from flask_sqlalchemy import Pagination, SQLAlchemy
from sqlalchemy.dialects.postgresql import insert, JSONB, UUID
from sqlalchemy.orm import Query
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.schema import Table


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


def paginate(
    query: Query,
    page: int,
    per_page: int,
    *,
    item_mapper: Optional[Mapper] = None,
) -> Pagination:
    """Return `per_page` items from page `page`."""
    if page < 1:
        page = 1

    if per_page < 1:
        raise ValueError('The number of items per page must be positive.')

    offset = (page - 1) * per_page

    items = query.limit(per_page).offset(offset).all()

    item_count = len(items)
    if page == 1 and item_count < per_page:
        total = item_count
    else:
        total = query.order_by(None).count()

    if item_mapper is not None:
        items = [item_mapper(item) for item in items]

    # Intentionally pass no query object.
    return Pagination(None, page, per_page, total, items)


def insert_ignore_on_conflict(table: Table, values: dict[str, Any]) -> None:
    """Insert the record identified by the primary key (specified as
    part of the values), or do nothing on conflict.
    """
    query = insert(table) \
        .values(**values) \
        .on_conflict_do_nothing(constraint=table.primary_key)

    db.session.execute(query)
    db.session.commit()


def upsert(
    table: Table, identifier: dict[str, Any], replacement: dict[str, Any]
) -> None:
    """Insert or update the record identified by `identifier` with value
    `replacement`.
    """
    execute_upsert(table, identifier, replacement)
    db.session.commit()


def upsert_many(
    table: Table,
    identifiers: Iterable[dict[str, Any]],
    replacement: dict[str, Any],
) -> None:
    """Insert or update the record identified by `identifier` with value
    `replacement`.
    """
    for identifier in identifiers:
        execute_upsert(table, identifier, replacement)

    db.session.commit()


def execute_upsert(
    table: Table, identifier: dict[str, Any], replacement: dict[str, Any]
) -> None:
    """Execute, but do not commit, an UPSERT."""
    query = _build_upsert_query(table, identifier, replacement)
    db.session.execute(query)


def _build_upsert_query(
    table: Table, identifier: dict[str, Any], replacement: dict[str, Any]
) -> Insert:
    values = identifier.copy()
    values.update(replacement)

    return insert(table) \
        .values(**values) \
        .on_conflict_do_update(
            constraint=table.primary_key,
            set_=replacement)
