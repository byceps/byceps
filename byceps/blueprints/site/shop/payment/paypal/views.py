"""
byceps.blueprints.site.shop.payment.paypal.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2020-2024 Jan Korneffel, Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from uuid import UUID

from flask import abort, current_app, g, jsonify, request
from paypalcheckoutsdk.orders import OrdersGetRequest
from paypalhttp import HttpError
from paypalhttp.http_response import Result as HttpResult
from pydantic import BaseModel, ValidationError

from byceps.paypal import paypal
from byceps.services.shop.order import order_command_service, order_service
from byceps.services.shop.order.email import order_email_service
from byceps.services.shop.order.models.order import Order
from byceps.signals import shop as shop_signals
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.views import create_empty_json_response


blueprint = create_blueprint('shop_payment_paypal', __name__)


class CapturePayPalRequest(BaseModel):
    shop_order_id: UUID
    paypal_order_id: str


@dataclass(frozen=True)
class PayPalOrderDetails:
    id: str
    transaction_id: str


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
        paypal_result = paypal.client.execute(request).result
    except HttpError as e:
        current_app.logger.error(
            'PayPal API returned status code %d for paypal_order_id = %s, shop_order_id = %s: %s',
            e.status_code,
            req.paypal_order_id,
            order.id,
            e.message,
        )
        return create_empty_json_response(400)

    paypal_order_details = _parse_paypal_order_details(paypal_result)

    if not _check_transaction_against_order(paypal_result, order):
        current_app.logger.error(
            'PayPal order %s failed verification against shop order %s',
            req.paypal_order_id,
            order.id,
        )
        return create_empty_json_response(400)

    _mark_order_as_paid(order, paypal_order_details)

    return jsonify({'status': 'OK'})


def _parse_request() -> CapturePayPalRequest:
    try:
        return CapturePayPalRequest.model_validate(request.get_json())
    except ValidationError as e:
        abort(400, e.json())


def _parse_paypal_order_details(result: HttpResult) -> PayPalOrderDetails:
    purchase_unit = result.purchase_units[0]

    return PayPalOrderDetails(
        id=result.id,
        transaction_id=_extract_transaction_id(purchase_unit),
    )


def _extract_transaction_id(purchase_unit) -> str:
    completed_captures = filter(
        lambda c: c.status in ('COMPLETED', 'PENDING'),
        purchase_unit.payments.captures,
    )

    transaction = next(completed_captures)

    return transaction.id


def _check_transaction_against_order(result: HttpResult, order: Order) -> bool:
    purchase_unit = result.purchase_units[0]

    return (
        result.status == 'COMPLETED'
        and purchase_unit.amount.currency_code == 'EUR'
        and purchase_unit.amount.value == str(order.total_amount)
        and purchase_unit.invoice_id == order.order_number
    )


def _mark_order_as_paid(
    order: Order, paypal_order_details: PayPalOrderDetails
) -> None:
    additional_payment_data = {
        'paypal_order_id': paypal_order_details.id,
        'paypal_transaction_id': paypal_order_details.transaction_id,
    }

    paid_order, event = order_command_service.mark_order_as_paid(
        order.id,
        'paypal',
        g.user,
        additional_payment_data=additional_payment_data,
    ).unwrap()

    order_email_service.send_email_for_paid_order_to_orderer(paid_order)

    shop_signals.order_paid.send(None, event=event)
