"""
byceps.announce.handlers.shop_order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce shop order events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask_babel import gettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.events.shop import (
    ShopOrderCanceledEvent,
    ShopOrderPaidEvent,
    ShopOrderPlacedEvent,
)
from byceps.services.shop.order import order_service
from byceps.services.webhooks.models import Announcement, OutgoingWebhook


@with_locale
def announce_order_placed(
    event: ShopOrderPlacedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that an order has been placed."""
    orderer_screen_name = get_screen_name_or_fallback(event.orderer_screen_name)

    text = gettext(
        '%(orderer_screen_name)s has placed order %(order_number)s.',
        orderer_screen_name=orderer_screen_name,
        order_number=event.order_number,
    )

    return Announcement(text)


@with_locale
def announce_order_paid(
    event: ShopOrderPaidEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that an order has been paid."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    orderer_screen_name = get_screen_name_or_fallback(event.orderer_screen_name)
    payment_method_label = order_service.find_payment_method_label(
        event.payment_method
    )

    text = gettext(
        '%(initiator_screen_name)s marked order %(order_number)s by %(orderer_screen_name)s as paid via %(payment_method_label)s.',
        initiator_screen_name=initiator_screen_name,
        order_number=event.order_number,
        orderer_screen_name=orderer_screen_name,
        payment_method_label=payment_method_label,
    )

    return Announcement(text)


@with_locale
def announce_order_canceled(
    event: ShopOrderCanceledEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that an order has been canceled."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    orderer_screen_name = get_screen_name_or_fallback(event.orderer_screen_name)

    text = gettext(
        '%(initiator_screen_name)s has canceled order %(order_number)s by %(orderer_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        order_number=event.order_number,
        orderer_screen_name=orderer_screen_name,
    )

    return Announcement(text)
