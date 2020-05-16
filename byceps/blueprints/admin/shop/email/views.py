"""
byceps.blueprints.admin.shop.email.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from decimal import Decimal

from flask import abort, current_app, Response

from .....config import ConfigurationError
from .....database import generate_uuid
from .....services.shop.order.email import service as shop_order_email_service
from .....services.shop.order.email.service import OrderEmailData
from .....services.shop.order.transfer.models import (
    Order,
    PaymentMethod,
    PaymentState,
)
from .....services.shop.shop import service as shop_service
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_error
from .....util.framework.templating import templated
from .....util.views import redirect_to

from ....authorization.decorators import permission_required
from ....authorization.registry import permission_registry

from ..shop.authorization import ShopPermission


blueprint = create_blueprint('shop_email_admin', __name__)


permission_registry.register_enum(ShopPermission)


@blueprint.route('/for_shop/<shop_id>')
@permission_required(ShopPermission.view)
@templated
def view_for_shop(shop_id):
    """Show e-mail examples."""
    shop = _get_shop_or_404(shop_id)

    return {
        'shop': shop,
    }


@blueprint.route('/for_shop/<shop_id>/example/order_placed')
@permission_required(ShopPermission.view)
def view_example_order_placed(shop_id):
    """Show example of order placed e-mail."""
    shop = _get_shop_or_404(shop_id)

    order = _build_order(shop.id, PaymentState.open, is_open=True)

    data = _build_email_data(order, shop)

    try:
        message = shop_order_email_service._assemble_email_for_incoming_order_to_orderer(
            data
        )
    except Exception as e:
        current_app.logger.error(
            f'Could not assemble example email for placed order:\n{e}'
        )
        flash_error(
            'Could not assemble example email. '
            'Are all necessary templates defined?'
        )
        return redirect_to('.view_for_shop', shop_id=shop.id)

    message_text = _render_message(message)
    return to_text_response(message_text)


@blueprint.route('/for_shop/<shop_id>/example/order_paid')
@permission_required(ShopPermission.view)
def view_example_order_paid(shop_id):
    """Show example of order paid e-mail."""
    shop = _get_shop_or_404(shop_id)

    order = _build_order(shop.id, PaymentState.paid, is_paid=True)

    data = _build_email_data(order, shop)

    try:
        message = shop_order_email_service._assemble_email_for_paid_order_to_orderer(
            data
        )
    except Exception as e:
        current_app.logger.error(
            f'Could not assemble example email for paid order:\n{e}'
        )
        flash_error(
            'Could not assemble example email. '
            'Are all necessary templates defined?'
        )
        return redirect_to('.view_for_shop', shop_id=shop.id)

    message_text = _render_message(message)
    return to_text_response(message_text)


@blueprint.route('/for_shop/<shop_id>/example/order_canceled')
@permission_required(ShopPermission.view)
def view_example_order_canceled(shop_id):
    """Show example of order canceled e-mail."""
    shop = _get_shop_or_404(shop_id)

    order = _build_order(
        shop.id,
        PaymentState.canceled_before_paid,
        is_canceled=True,
        cancelation_reason='Kein fristgerechter Geldeingang feststellbar',
    )

    data = _build_email_data(order, shop)

    try:
        message = shop_order_email_service._assemble_email_for_canceled_order_to_orderer(
            data
        )
    except Exception as e:
        current_app.logger.error(
            f'Could not assemble example email for canceled order:\n{e}'
        )
        flash_error(
            'Could not assemble example email. '
            'Are all necessary templates defined?'
        )
        return redirect_to('.view_for_shop', shop_id=shop.id)

    message_text = _render_message(message)
    return to_text_response(message_text)


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop


def _build_order(
    shop_id,
    payment_state,
    *,
    is_open=False,
    is_canceled=False,
    is_paid=False,
    cancelation_reason=None,
) -> Order:
    order_id = generate_uuid()
    order_number = 'AWSM-ORDR-9247'

    created_at = datetime.utcnow()
    placed_by_id = None

    first_names = 'Bella-Bernadine'
    last_name = 'Ballerwurm'
    address = None

    total_amount = Decimal('42.95')
    items = []
    payment_method = PaymentMethod.bank_transfer

    return Order(
        order_id,
        shop_id,
        order_number,
        created_at,
        placed_by_id,
        first_names,
        last_name,
        address,
        total_amount,
        items,
        payment_method,
        payment_state,
        is_open,
        is_canceled,
        is_paid,
        False,  # is_invoiced
        False,  # is_shipping_required
        False,  # is_shipped
        cancelation_reason,
    )


def _build_email_data(order, shop) -> OrderEmailData:
    return OrderEmailData(
        order=order,
        email_config_id=shop.email_config_id,
        orderer_screen_name='Besteller',
        orderer_email_address='besteller@example.com',
    )


def _render_message(message) -> str:
    if not message.sender:
        raise ConfigurationError(
            'No e-mail sender address configured for message.'
        )

    return (
        f'From: {message.sender}\n'
        f'To: {message.recipients}\n'
        f'Subject: {message.subject}\n'
        f'\n\n{message.body}\n'
    )


def to_text_response(text: str) -> Response:
    return Response(text, mimetype='text/plain')
