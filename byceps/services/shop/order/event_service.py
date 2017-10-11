"""
byceps.services.shop.order.event_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from ....database import db

from .models.order import OrderID
from .models.order_event import OrderEvent, OrderEventData


def create_event(event_type: str, order_id: OrderID, data: OrderEventData
                ) -> None:
    """Create an order event."""
    event = _build_event(event_type, order_id, data)

    db.session.add(event)
    db.session.commit()


def _build_event(event_type: str, order_id: OrderID, data: OrderEventData
                ) -> OrderEvent:
    """Assemble, but not persist, an order event."""
    now = datetime.utcnow()

    return OrderEvent(now, event_type, order_id, data)
