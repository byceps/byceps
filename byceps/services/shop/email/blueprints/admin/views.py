"""
byceps.services.shop.email.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g

from byceps.services.brand import brand_service
from byceps.services.brand.models import Brand
from byceps.services.email import email_config_service
from byceps.services.email.models import NameAndAddress
from byceps.services.shop.order.email import order_email_example_service
from byceps.services.shop.shop import shop_service
from byceps.services.shop.shop.models import Shop
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated
from byceps.util.l10n import get_user_locale
from byceps.util.result import Result
from byceps.util.views import permission_required


blueprint = create_blueprint('shop_email_admin', __name__)


@blueprint.get('/for_shop/<shop_id>')
@permission_required('shop.view')
@templated
def view_for_shop(shop_id):
    """Show e-mail examples."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    email_config = email_config_service.get_config(brand.id)
    sender = email_config.sender

    example_placed_order_message_text = _get_example_placed_order_message_text(
        shop, sender, brand
    )
    example_paid_order_message_text = _get_example_paid_order_message_text(
        shop, sender, brand
    )
    example_canceled_order_message_text = (
        _get_example_canceled_order_message_text(shop, sender, brand)
    )

    return {
        'shop': shop,
        'brand': brand,
        'email_config': email_config,
        'placed_order_message_text_result': example_placed_order_message_text,
        'paid_order_message_text_result': example_paid_order_message_text,
        'canceled_order_message_text_result': example_canceled_order_message_text,
    }


def _get_example_placed_order_message_text(
    shop: Shop, sender: NameAndAddress, brand: Brand
) -> Result[str, str]:
    locale = get_user_locale(g.user)
    return order_email_example_service.build_example_placed_order_message_text(
        shop, sender, brand, locale
    )


def _get_example_paid_order_message_text(
    shop: Shop, sender: NameAndAddress, brand: Brand
) -> Result[str, str]:
    locale = get_user_locale(g.user)
    return order_email_example_service.build_example_paid_order_message_text(
        shop, sender, brand, locale
    )


def _get_example_canceled_order_message_text(
    shop: Shop, sender: NameAndAddress, brand: Brand
) -> Result[str, str]:
    locale = get_user_locale(g.user)
    return (
        order_email_example_service.build_example_canceled_order_message_text(
            shop, sender, brand, locale
        )
    )


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop
