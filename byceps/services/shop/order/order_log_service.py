"""
byceps.services.shop.order.order_log_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Iterable, Optional

from sqlalchemy import select

from ....database import db
from ....typing import UserID

from ..shop.models import ShopID

from .dbmodels.log import DbOrderLogEntry
from .dbmodels.order import DbOrder
from .models.log import OrderLogEntry, OrderLogEntryData
from .models.order import OrderID


def create_entry(
    event_type: str,
    order_id: OrderID,
    data: OrderLogEntryData,
    *,
    occurred_at: Optional[datetime] = None,
) -> None:
    """Create an order log entry."""
    db_entry = build_entry(event_type, order_id, data, occurred_at=occurred_at)

    db.session.add(db_entry)
    db.session.commit()


def create_entries(
    event_type: str, order_id: OrderID, datas: Iterable[OrderLogEntryData]
) -> None:
    """Create a sequence of order log entries."""
    db_entries = [build_entry(event_type, order_id, data) for data in datas]

    db.session.add_all(db_entries)
    db.session.commit()


def build_entry(
    event_type: str,
    order_id: OrderID,
    data: OrderLogEntryData,
    *,
    occurred_at: Optional[datetime] = None,
) -> DbOrderLogEntry:
    """Assemble, but not persist, an order log entry."""
    if occurred_at is None:
        occurred_at = datetime.utcnow()

    return DbOrderLogEntry(occurred_at, event_type, order_id, data)


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
