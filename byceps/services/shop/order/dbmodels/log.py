"""
byceps.services.shop.order.dbmodels.log
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.shop.order.models.log import OrderLogEntryData
from byceps.services.shop.order.models.order import OrderID
from byceps.util.instances import ReprBuilder


class DbOrderLogEntry(db.Model):
    """A log entry regarding an order."""

    __tablename__ = 'shop_order_log_entries'

    id: Mapped[UUID] = mapped_column(db.Uuid, primary_key=True)
    occurred_at: Mapped[datetime]
    event_type: Mapped[str] = mapped_column(db.UnicodeText, index=True)
    order_id: Mapped[OrderID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_orders.id'), index=True
    )
    data: Mapped[OrderLogEntryData] = mapped_column(db.JSONB)

    def __init__(
        self,
        entry_id: UUID,
        occurred_at: datetime,
        event_type: str,
        order_id: OrderID,
        data: OrderLogEntryData,
    ) -> None:
        self.id = entry_id
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
