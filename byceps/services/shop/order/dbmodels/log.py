"""
byceps.services.shop.order.dbmodels.log
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.database import db, generate_uuid7
from byceps.services.shop.order.models.log import OrderLogEntryData
from byceps.services.shop.order.models.order import OrderID
from byceps.util.instances import ReprBuilder


class DbOrderLogEntry(db.Model):
    """A log entry regarding an order."""

    __tablename__ = 'shop_order_log_entries'

    id = db.Column(db.Uuid, default=generate_uuid7, primary_key=True)
    occurred_at = db.Column(db.DateTime, nullable=False)
    event_type = db.Column(db.UnicodeText, index=True, nullable=False)
    order_id = db.Column(
        db.Uuid, db.ForeignKey('shop_orders.id'), index=True, nullable=False
    )
    data = db.Column(db.JSONB)

    def __init__(
        self,
        occurred_at: datetime,
        event_type: str,
        order_id: OrderID,
        data: OrderLogEntryData,
    ) -> None:
        self.occurred_at = occurred_at
        self.event_type = event_type
        self.order_id = order_id
        self.data = data

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_custom(repr(self.event_type))
            .add_with_lookup('order_id')
            .add_with_lookup('data')
            .build()
        )
