"""
byceps.announce.handlers.shop_order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce shop order events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from ...services.webhooks.models import OutgoingWebhook

from ..helpers import Announcement
from ..text_assembly import shop_order


def announce_order_placed(
    event: ShopOrderPlaced, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that an order has been placed."""
    text = shop_order.assemble_text_for_order_placed(event)
    return Announcement(text)


def announce_order_paid(
    event: ShopOrderPaid, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that an order has been paid."""
    text = shop_order.assemble_text_for_order_paid(event)
    return Announcement(text)


def announce_order_canceled(
    event: ShopOrderCanceled, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that an order has been canceled."""
    text = shop_order.assemble_text_for_order_canceled(event)
    return Announcement(text)
