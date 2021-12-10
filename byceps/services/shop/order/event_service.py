"""
byceps.services.shop.order.event_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
from typing import Any, Optional, Sequence

from sqlalchemy import select

from ....database import db
from ....typing import UserID

from .dbmodels.order_event import OrderEvent as DbOrderEvent
from .transfer.models.event import OrderEvent, OrderEventData
from .transfer.models.order import OrderID


def create_event(
    event_type: str,
    order_id: OrderID,
    data: OrderEventData,
    *,
    occurred_at: Optional[datetime] = None,
) -> None:
    """Create an order event."""
    event = build_event(event_type, order_id, data, occurred_at=occurred_at)

    db.session.add(event)
    db.session.commit()


def create_events(
    event_type: str, order_id: OrderID, datas: Sequence[OrderEventData]
) -> None:
    """Create a sequence of order events."""
    events = [build_event(event_type, order_id, data) for data in datas]

    db.session.add_all(events)
    db.session.commit()


def build_event(
    event_type: str,
    order_id: OrderID,
    data: OrderEventData,
    *,
    occurred_at: Optional[datetime] = None,
) -> DbOrderEvent:
    """Assemble, but not persist, an order event."""
    if occurred_at is None:
        occurred_at = datetime.utcnow()

    return DbOrderEvent(occurred_at, event_type, order_id, data)


def get_events_for_order(order_id: OrderID) -> list[OrderEvent]:
    """Return the events for that order."""
    db_events = db.session.execute(
        select(DbOrderEvent)
        .filter_by(order_id=order_id)
        .order_by(DbOrderEvent.occurred_at)
    ).scalars().all()

    return [_db_entity_to_event(db_event) for db_event in db_events]


def get_events_of_types_by_initiator(
    event_types: frozenset[str], initiator_id: UserID
) -> list[OrderEvent]:
    """Return the events of these types initiated by the user."""
    if not event_types:
        return []

    db_events = db.session.execute(
        select(DbOrderEvent)
        .filter(DbOrderEvent.event_type.in_(event_types))
        .filter(DbOrderEvent.data['initiator_id'].astext == str(initiator_id))
        .order_by(DbOrderEvent.occurred_at)
    ).scalars().all()

    return [_db_entity_to_event(db_event) for db_event in db_events]


def _db_entity_to_event(db_event: DbOrderEvent) -> OrderEvent:
    return OrderEvent(
        id=db_event.id,
        occurred_at=db_event.occurred_at,
        event_type=db_event.event_type,
        order_id=db_event.order_id,
        data=db_event.data.copy(),
    )
