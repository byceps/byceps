"""
byceps.announce.irc.shop_order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce shop order events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.shop import (
    _ShopOrderEvent,
    ShopOrderCanceled,
    ShopOrderPaid,
    ShopOrderPlaced,
)

from ..common import shop_order

from ._util import send_message


def announce_order_placed(event: ShopOrderPlaced) -> None:
    """Announce that an order has been placed."""
    text = shop_order.assemble_text_for_order_placed(event)

    send_shop_message(event, text)


def announce_order_paid(event: ShopOrderPaid) -> None:
    """Announce that an order has been paid."""
    text = shop_order.assemble_text_for_order_paid(event)

    send_shop_message(event, text)


def announce_order_canceled(event: ShopOrderCanceled) -> None:
    """Announce that an order has been canceled."""
    text = shop_order.assemble_text_for_order_canceled(event)

    send_shop_message(event, text)


# helpers


def send_shop_message(event: _ShopOrderEvent, text: str) -> None:
    scope = 'shop'
    scope_id = None

    send_message(event, scope, scope_id, text)
