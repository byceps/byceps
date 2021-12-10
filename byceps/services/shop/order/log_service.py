"""
byceps.services.shop.order.log_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
from typing import Any, Optional, Sequence

from sqlalchemy import select

from ....database import db
from ....typing import UserID

from .dbmodels.log import OrderLogEntry as DbOrderLogEntry
from .transfer.models.log import OrderLogEntry, OrderLogEntryData
from .transfer.models.order import OrderID


def create_entry(
    event_type: str,
    order_id: OrderID,
    data: OrderLogEntryData,
    *,
    occurred_at: Optional[datetime] = None,
) -> None:
    """Create an order log entry."""
    entry = build_log_entry(event_type, order_id, data, occurred_at=occurred_at)

    db.session.add(entry)
    db.session.commit()


def create_entries(
    event_type: str, order_id: OrderID, datas: Sequence[OrderLogEntryData]
) -> None:
    """Create a sequence of order log entries."""
    entries = [build_log_entry(event_type, order_id, data) for data in datas]

    db.session.add_all(entries)
    db.session.commit()


def build_log_entry(
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
    db_entries = db.session.execute(
        select(DbOrderLogEntry)
        .filter_by(order_id=order_id)
        .order_by(DbOrderLogEntry.occurred_at)
    ).scalars().all()

    return [_db_entity_to_entry(db_entry) for db_entry in db_entries]


def get_entries_of_types_by_initiator(
    event_types: frozenset[str], initiator_id: UserID
) -> list[OrderLogEntry]:
    """Return the log entries of these types initiated by the user."""
    if not event_types:
        return []

    db_entries = db.session.execute(
        select(DbOrderLogEntry)
        .filter(DbOrderLogEntry.event_type.in_(event_types))
        .filter(DbOrderLogEntry.data['initiator_id'].astext == str(initiator_id))
        .order_by(DbOrderLogEntry.occurred_at)
    ).scalars().all()

    return [_db_entity_to_entry(db_entry) for db_entry in db_entries]


def _db_entity_to_entry(db_entry: DbOrderLogEntry) -> OrderLogEntry:
    return OrderLogEntry(
        id=db_entry.id,
        occurred_at=db_entry.occurred_at,
        event_type=db_entry.event_type,
        order_id=db_entry.order_id,
        data=db_entry.data.copy(),
    )
