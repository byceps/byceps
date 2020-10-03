"""
byceps.announce.irc.shop_order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce shop order events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from ...services.shop.order import service as order_service
from ...signals import shop as shop_signals
from ...util.irc import send_message
from ...util.jobqueue import enqueue

from ..helpers import get_screen_name_or_fallback

from ._config import CHANNEL_ORGA_LOG


@shop_signals.order_placed.connect
def _on_order_placed(
    sender, *, event: Optional[ShopOrderPlaced] = None
) -> None:
    enqueue(announce_order_placed, event)


def announce_order_placed(event: ShopOrderPlaced) -> None:
    """Announce that an order has been placed."""
    orderer_screen_name = get_screen_name_or_fallback(event.orderer_screen_name)

    text = (
        f'{orderer_screen_name} hat Bestellung {event.order_number} aufgegeben.'
    )

    send_message(CHANNEL_ORGA_LOG, text)


@shop_signals.order_paid.connect
def _on_order_paid(sender, *, event: Optional[ShopOrderPaid] = None) -> None:
    enqueue(announce_order_paid, event)


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

    send_message(CHANNEL_ORGA_LOG, text)


@shop_signals.order_canceled.connect
def _on_order_canceled(
    sender, *, event: Optional[ShopOrderCanceled] = None
) -> None:
    enqueue(announce_order_canceled, event)


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

    send_message(CHANNEL_ORGA_LOG, text)
