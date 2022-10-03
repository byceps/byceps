"""
byceps.announce.text_assembly.shop_order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce shop order events.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from ...events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from ...services.shop.order import order_service

from ._helpers import get_screen_name_or_fallback, with_locale


@with_locale
def assemble_text_for_order_placed(event: ShopOrderPlaced) -> str:
    orderer_screen_name = get_screen_name_or_fallback(event.orderer_screen_name)

    return gettext(
        '%(orderer_screen_name)s has placed order %(order_number)s.',
        orderer_screen_name=orderer_screen_name,
        order_number=event.order_number,
    )


@with_locale
def assemble_text_for_order_paid(event: ShopOrderPaid) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    orderer_screen_name = get_screen_name_or_fallback(event.orderer_screen_name)
    payment_method_label = order_service.find_payment_method_label(
        event.payment_method
    )

    return gettext(
        '%(initiator_screen_name)s marked order %(order_number)s by %(orderer_screen_name)s as paid via %(payment_method_label)s.',
        initiator_screen_name=initiator_screen_name,
        order_number=event.order_number,
        orderer_screen_name=orderer_screen_name,
        payment_method_label=payment_method_label,
    )


@with_locale
def assemble_text_for_order_canceled(event: ShopOrderCanceled) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    orderer_screen_name = get_screen_name_or_fallback(event.orderer_screen_name)

    return gettext(
        '%(initiator_screen_name)s has canceled order %(order_number)s by %(orderer_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        order_number=event.order_number,
        orderer_screen_name=orderer_screen_name,
    )
