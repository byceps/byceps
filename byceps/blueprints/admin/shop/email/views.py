"""
byceps.blueprints.admin.shop.email.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from flask import abort, current_app, g

from .....services.brand import brand_service
from .....services.email import email_config_service
from .....services.shop.order.email import order_email_example_service
from .....services.shop.shop import shop_service
from .....util.framework.blueprint import create_blueprint
from .....util.framework.templating import templated
from .....util.views import permission_required


blueprint = create_blueprint('shop_email_admin', __name__)


@blueprint.get('/for_shop/<shop_id>')
@permission_required('shop.view')
@templated
def view_for_shop(shop_id):
    """Show e-mail examples."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    email_config = email_config_service.get_config(shop.brand_id)

    example_placed_order_message_text = _get_example_placed_order_message_text(
        shop.id
    )
    example_paid_order_message_text = _get_example_paid_order_message_text(
        shop.id
    )
    example_canceled_order_message_text = (
        _get_example_canceled_order_message_text(shop.id)
    )

    return {
        'shop': shop,
        'brand': brand,
        'email_config': email_config,
        'placed_order_message_text': example_placed_order_message_text,
        'paid_order_message_text': example_paid_order_message_text,
        'canceled_order_message_text': example_canceled_order_message_text,
    }


def _get_example_placed_order_message_text(shop_id) -> Optional[str]:
    try:
        return (
            order_email_example_service.build_example_placed_order_message_text(
                shop_id, g.user.locale
            )
        )
    except order_email_example_service.EmailAssemblyFailed as e:
        current_app.logger.error(
            f'Could not assemble example email for placed order:\n{e}'
        )
        return None


def _get_example_paid_order_message_text(shop_id) -> Optional[str]:
    try:
        return (
            order_email_example_service.build_example_paid_order_message_text(
                shop_id, g.user.locale
            )
        )
    except order_email_example_service.EmailAssemblyFailed as e:
        current_app.logger.error(
            f'Could not assemble example email for paid order:\n{e}'
        )
        return None


def _get_example_canceled_order_message_text(shop_id) -> Optional[str]:
    try:
        return order_email_example_service.build_example_canceled_order_message_text(
            shop_id, g.user.locale
        )
    except order_email_example_service.EmailAssemblyFailed as e:
        current_app.logger.error(
            f'Could not assemble example email for canceled order:\n{e}'
        )
        return None


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop
