"""
byceps.announce.text_assembly.shop_order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce shop order events.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from ...services.shop.order import service as order_service

from ._helpers import get_screen_name_or_fallback


def assemble_text_for_order_placed(event: ShopOrderPlaced) -> str:
    orderer_screen_name = get_screen_name_or_fallback(event.orderer_screen_name)

    return (
        f'{orderer_screen_name} hat Bestellung {event.order_number} aufgegeben.'
    )


def assemble_text_for_order_paid(event: ShopOrderPaid) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    orderer_screen_name = get_screen_name_or_fallback(event.orderer_screen_name)
    payment_method_label = order_service.find_payment_method_label(
        event.payment_method
    )

    return (
        f'{initiator_screen_name} hat Bestellung {event.order_number} '
        f'von {orderer_screen_name} als per {payment_method_label} bezahlt '
        'markiert.'
    )


def assemble_text_for_order_canceled(event: ShopOrderCanceled) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    orderer_screen_name = get_screen_name_or_fallback(event.orderer_screen_name)

    return (
        f'{initiator_screen_name} hat Bestellung {event.order_number} '
        f'von {orderer_screen_name} storniert.'
    )
