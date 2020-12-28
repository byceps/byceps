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
from ...services.shop.order import service as order_service

from ..helpers import get_screen_name_or_fallback

from ._util import send_message


def announce_order_placed(event: ShopOrderPlaced) -> None:
    """Announce that an order has been placed."""
    orderer_screen_name = get_screen_name_or_fallback(event.orderer_screen_name)

    text = (
        f'{orderer_screen_name} hat Bestellung {event.order_number} aufgegeben.'
    )

    send_shop_message(event, text)


def announce_order_paid(event: ShopOrderPaid) -> None:
    """Announce that an order has been paid."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    orderer_screen_name = get_screen_name_or_fallback(event.orderer_screen_name)
    payment_method_label = order_service.find_payment_method_label(
        event.payment_method
    )

    text = (
        f'{initiator_screen_name} hat Bestellung {event.order_number} '
        f'von {orderer_screen_name} als per {payment_method_label} bezahlt '
        'markiert.'
    )

    send_shop_message(event, text)


def announce_order_canceled(event: ShopOrderCanceled) -> None:
    """Announce that an order has been canceled."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    orderer_screen_name = get_screen_name_or_fallback(event.orderer_screen_name)

    text = (
        f'{initiator_screen_name} hat Bestellung {event.order_number} '
        f'von {orderer_screen_name} storniert.'
    )

    send_shop_message(event, text)


# helpers


def send_shop_message(event: _ShopOrderEvent, text: str) -> None:
    scope = 'shop'
    scope_id = None

    send_message(event, scope, scope_id, text)
