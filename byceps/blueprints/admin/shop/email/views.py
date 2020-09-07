"""
byceps.blueprints.admin.shop.email.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, current_app, Response

from .....services.email import service as email_service
from .....services.shop.order.email import (
    example_service as example_order_email_service,
)
from .....services.shop.shop import service as shop_service
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_error
from .....util.framework.templating import templated
from .....util.views import redirect_to

from ....common.authorization.decorators import permission_required
from ....common.authorization.registry import permission_registry

from ..shop.authorization import ShopPermission


blueprint = create_blueprint('shop_email_admin', __name__)


permission_registry.register_enum(ShopPermission)


@blueprint.route('/for_shop/<shop_id>')
@permission_required(ShopPermission.view)
@templated
def view_for_shop(shop_id):
    """Show e-mail examples."""
    shop = _get_shop_or_404(shop_id)

    email_config = email_service.find_config(shop.email_config_id)

    return {
        'shop': shop,
        'email_config': email_config,
    }


@blueprint.route('/for_shop/<shop_id>/example/order_placed')
@permission_required(ShopPermission.view)
def view_example_order_placed(shop_id):
    """Show example of order placed e-mail."""
    shop = _get_shop_or_404(shop_id)

    try:
        message_text = (
            example_order_email_service.build_example_placed_order_message_text(
                shop.id
            )
        )
    except example_order_email_service.EmailAssemblyFailed as e:
        current_app.logger.error(
            f'Could not assemble example email for placed order:\n{e}'
        )
        flash_error(
            'Could not assemble example email. '
            'Are all necessary templates defined?'
        )
        return redirect_to('.view_for_shop', shop_id=shop.id)

    return to_text_response(message_text)


@blueprint.route('/for_shop/<shop_id>/example/order_paid')
@permission_required(ShopPermission.view)
def view_example_order_paid(shop_id):
    """Show example of order paid e-mail."""
    shop = _get_shop_or_404(shop_id)

    try:
        message_text = (
            example_order_email_service.build_example_paid_order_message_text(
                shop.id
            )
        )
    except example_order_email_service.EmailAssemblyFailed as e:
        current_app.logger.error(
            f'Could not assemble example email for paid order:\n{e}'
        )
        flash_error(
            'Could not assemble example email. '
            'Are all necessary templates defined?'
        )
        return redirect_to('.view_for_shop', shop_id=shop.id)

    return to_text_response(message_text)


@blueprint.route('/for_shop/<shop_id>/example/order_canceled')
@permission_required(ShopPermission.view)
def view_example_order_canceled(shop_id):
    """Show example of order canceled e-mail."""
    shop = _get_shop_or_404(shop_id)

    try:
        message_text = example_order_email_service.build_example_canceled_order_message_text(
            shop.id
        )
    except example_order_email_service.EmailAssemblyFailed as e:
        current_app.logger.error(
            f'Could not assemble example email for canceled order:\n{e}'
        )
        flash_error(
            'Could not assemble example email. '
            'Are all necessary templates defined?'
        )
        return redirect_to('.view_for_shop', shop_id=shop.id)

    return to_text_response(message_text)


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop


def to_text_response(text: str) -> Response:
    return Response(text, mimetype='text/plain')
