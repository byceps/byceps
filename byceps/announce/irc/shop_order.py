"""
byceps.announce.irc.shop_order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce shop order events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...blueprints.shop.order import signals
from ...events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from ...services.shop.order import service as order_service
from ...services.user import service as user_service
from ...typing import UserID
from ...util.irc import send_message
from ...util.jobqueue import enqueue

from ._config import CHANNEL_ORGA_LOG, CHANNEL_PUBLIC


@signals.order_placed.connect
def _on_order_placed(sender, *, event: ShopOrderPlaced) -> None:
    enqueue(announce_order_placed, event)


def announce_order_placed(event: ShopOrderPlaced) -> None:
    """Announce that an order has been placed."""
    channels = [CHANNEL_ORGA_LOG]

    order = order_service.find_order(event.order_id)

    screen_name = _get_screen_name(order.placed_by_id)

    text = f'{screen_name} hat Bestellung {order.order_number} aufgegeben.'

    send_message(channels, text)


@signals.order_paid.connect
def _on_order_paid(sender, *, event: ShopOrderPaid) -> None:
    enqueue(announce_order_paid, event)


def announce_order_paid(event: ShopOrderPaid) -> None:
    """Announce that an order has been paid."""
    channels = [CHANNEL_ORGA_LOG]

    order = order_service.find_order(event.order_id)

    initiator_screen_name = _get_screen_name(event.initiator_id)
    orderer_screen_name = _get_screen_name(order.placed_by_id)

    text = (
        f'{initiator_screen_name} hat Bestellung {order.order_number} '
        f'von {orderer_screen_name} als bezahlt markiert.'
    )

    send_message(channels, text)


@signals.order_canceled.connect
def _on_order_canceled(sender, *, event: ShopOrderCanceled) -> None:
    enqueue(announce_order_canceled, event)


def announce_order_canceled(event: ShopOrderCanceled) -> None:
    """Announce that an order has been canceled."""
    channels = [CHANNEL_ORGA_LOG]

    order = order_service.find_order(event.order_id)

    initiator_screen_name = _get_screen_name(event.initiator_id)
    orderer_screen_name = _get_screen_name(order.placed_by_id)

    text = (
        f'{initiator_screen_name} hat Bestellung {order.order_number} '
        f'von {orderer_screen_name} storniert.'
    )

    send_message(channels, text)


def _get_screen_name(user_id: UserID) -> str:
    return user_service.find_screen_name(user_id)
