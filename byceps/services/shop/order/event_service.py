"""
byceps.services.shop.order.event_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
from typing import Sequence

from ....database import db

from .dbmodels.order_event import OrderEvent as DbOrderEvent, OrderEventData
from .transfer.models.order import OrderID


def create_event(
    event_type: str, order_id: OrderID, data: OrderEventData
) -> None:
    """Create an order event."""
    event = build_event(event_type, order_id, data)

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
    event_type: str, order_id: OrderID, data: OrderEventData
) -> DbOrderEvent:
    """Assemble, but not persist, an order event."""
    now = datetime.utcnow()

    return DbOrderEvent(now, event_type, order_id, data)


def get_events_for_order(order_id: OrderID) -> list[DbOrderEvent]:
    """Return the events for that order."""
    return db.session \
        .query(DbOrderEvent) \
        .filter_by(order_id=order_id) \
        .order_by(DbOrderEvent.occurred_at) \
        .all()
