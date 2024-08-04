"""
byceps.blueprints.site.shop.payment.paypal.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2020 Jan Korneffel
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from flask import abort, current_app, g, jsonify, request
from paypalcheckoutsdk.orders import OrdersGetRequest
from paypalhttp import HttpError
from pydantic import BaseModel, ValidationError

from byceps.paypal import paypal
from byceps.services.shop.order import order_service
from byceps.services.shop.order.email import order_email_service
from byceps.signals import shop as shop_signals
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.views import create_empty_json_response


blueprint = create_blueprint('shop_payment_paypal', __name__)


class CapturePayPalRequest(BaseModel):
    shop_order_id: UUID
    paypal_order_id: str


@blueprint.post('/capture')
def capture_transaction():
    """Reconcile PayPal transaction."""
    if not g.user.authenticated:
        return create_empty_json_response(403)

    req = _parse_request()

    order = order_service.find_order(req.shop_order_id)
    if not order or not order.is_open:
        return create_empty_json_response(400)

    request = OrdersGetRequest(req.paypal_order_id)
    try:
        response = paypal.client.execute(request)
    except HttpError as e:
        current_app.logger.error(
            'PayPal API returned status code %d for paypal_order_id = %s, shop_order_id = %s: %s',
            e.status_code,
            req.paypal_order_id,
            order.id,
            e.message,
        )
        return create_empty_json_response(400)

    if not _check_transaction_against_order(response, order):
        current_app.logger.error(
            'PayPal order %s failed verification against shop order %s',
            req.paypal_order_id,
            order.id,
        )
        return create_empty_json_response(400)

    paid_order, event = order_service.mark_order_as_paid(
        order.id,
        'paypal',
        g.user,
        additional_payment_data={
            'paypal_order_id': response.result.id,
            'paypal_transaction_id': _extract_transaction_id(response),
        },
    ).unwrap()

    order_email_service.send_email_for_paid_order_to_orderer(paid_order)

    shop_signals.order_paid.send(None, event=event)

    return jsonify({'status': 'OK'})


def _check_transaction_against_order(response, order):
    purchase_unit = response.result.purchase_units[0]

    return (
        response.result.status == 'COMPLETED'
        and purchase_unit.amount.currency_code == 'EUR'
        and purchase_unit.amount.value == str(order.total_amount)
        and purchase_unit.invoice_id == order.order_number
    )


def _extract_transaction_id(response):
    purchase_unit = response.result.purchase_units[0]

    completed_captures = filter(
        lambda c: c.status in ('COMPLETED', 'PENDING'),
        purchase_unit.payments.captures,
    )
    transaction = next(completed_captures)

    return transaction.id


def _parse_request() -> CapturePayPalRequest:
    try:
        return CapturePayPalRequest.model_validate(request.get_json())
    except ValidationError as e:
        abort(400, e.json())
