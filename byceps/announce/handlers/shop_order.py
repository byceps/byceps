"""
byceps.announce.handlers.shop_order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce shop order events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from flask_babel import gettext

from ...events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from ...services.shop.order import order_service
from ...services.webhooks.models import OutgoingWebhook

from ..helpers import Announcement, get_screen_name_or_fallback, with_locale


@with_locale
def announce_order_placed(
    event: ShopOrderPlaced, webhook: OutgoingWebhook
) -> Optional[Announcement]:
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
    event: ShopOrderPaid, webhook: OutgoingWebhook
) -> Optional[Announcement]:
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
    event: ShopOrderCanceled, webhook: OutgoingWebhook
) -> Optional[Announcement]:
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
