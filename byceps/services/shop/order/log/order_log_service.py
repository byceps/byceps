"""
byceps.services.shop.order.log.order_log_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable

from sqlalchemy import select

from byceps.database import db
from byceps.services.shop.order.dbmodels.order import DbOrder
from byceps.services.shop.order.models.order import OrderID
from byceps.services.shop.shop.models import ShopID
from byceps.services.user.models.user import UserID

from .dbmodels import DbOrderLogEntry
from .models import OrderLogEntry


def persist_entry(entry: OrderLogEntry) -> None:
    """Store an order log entry."""
    db_entry = to_db_entry(entry)
    db.session.add(db_entry)
    db.session.commit()


def persist_entries(entries: Iterable[OrderLogEntry]) -> None:
    """Store multiple order log entries."""
    db_entries = [to_db_entry(entry) for entry in entries]
    db.session.add_all(db_entries)
    db.session.commit()


def to_db_entry(entry: OrderLogEntry) -> DbOrderLogEntry:
    """Convert log entry to database entity."""
    return DbOrderLogEntry(
        entry.id,
        entry.occurred_at,
        entry.event_type,
        entry.order_id,
        entry.data,
    )


def get_entries_for_order(order_id: OrderID) -> list[OrderLogEntry]:
    """Return the log entries for that order."""
    db_entries = db.session.scalars(
        select(DbOrderLogEntry)
        .filter_by(order_id=order_id)
        .order_by(DbOrderLogEntry.occurred_at)
    ).all()

    return [_db_entity_to_entry(db_entry) for db_entry in db_entries]


def get_entries_of_type_for_order(
    order_id: OrderID, event_type: str
) -> list[OrderLogEntry]:
    """Return the log entries of that type for that order."""
    db_entries = db.session.scalars(
        select(DbOrderLogEntry)
        .filter_by(order_id=order_id)
        .filter_by(event_type=event_type)
        .order_by(DbOrderLogEntry.occurred_at)
    ).all()

    return [_db_entity_to_entry(db_entry) for db_entry in db_entries]


def get_entries_by_initiator(
    initiator_id: UserID, event_types: frozenset[str]
) -> list[OrderLogEntry]:
    """Return the log entries of these types initiated by the user."""
    if not event_types:
        return []

    db_entries = db.session.scalars(
        select(DbOrderLogEntry)
        .filter(DbOrderLogEntry.event_type.in_(event_types))
        .filter(
            DbOrderLogEntry.data['initiator_id'].astext == str(initiator_id)
        )
        .order_by(DbOrderLogEntry.occurred_at)
    ).all()

    return [_db_entity_to_entry(db_entry) for db_entry in db_entries]


def get_latest_entries_for_shop(
    shop_id: ShopID, event_types: frozenset[str], limit: int
) -> list[OrderLogEntry]:
    """Return the most recent log entries of these types for that shop."""
    if not event_types:
        return []

    db_entries = db.session.scalars(
        select(DbOrderLogEntry)
        .join(DbOrder)
        .filter(DbOrder.shop_id == shop_id)
        .filter(DbOrderLogEntry.event_type.in_(event_types))
        .order_by(DbOrderLogEntry.occurred_at.desc())
        .limit(limit)
    ).all()

    return [_db_entity_to_entry(db_entry) for db_entry in db_entries]


def _db_entity_to_entry(db_entry: DbOrderLogEntry) -> OrderLogEntry:
    return OrderLogEntry(
        id=db_entry.id,
        occurred_at=db_entry.occurred_at,
        event_type=db_entry.event_type,
        order_id=db_entry.order_id,
        data=db_entry.data.copy(),
    )
