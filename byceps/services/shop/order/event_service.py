"""
byceps.services.shop.order.event_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Sequence

from ....database import db

from .models.order import OrderID
from .models.order_event import OrderEvent, OrderEventData


def create_event(event_type: str, order_id: OrderID, data: OrderEventData
                ) -> None:
    """Create an order event."""
    event = _build_event(event_type, order_id, data)

    db.session.add(event)
    db.session.commit()


def create_events(event_type: str, order_id: OrderID,
                  datas: Sequence[OrderEventData]) -> None:
    """Create a sequence of order events."""
    events = [_build_event(event_type, order_id, data) for data in datas]

    db.session.add_all(events)
    db.session.commit()


def _build_event(event_type: str, order_id: OrderID, data: OrderEventData
                ) -> OrderEvent:
    """Assemble, but not persist, an order event."""
    now = datetime.utcnow()

    return OrderEvent(now, event_type, order_id, data)


def get_events_for_order(order_id: OrderID) -> Sequence[OrderEvent]:
    """Return the events for that order."""
    return OrderEvent.query \
        .filter_by(order_id=order_id) \
        .order_by(OrderEvent.occurred_at) \
        .all()
