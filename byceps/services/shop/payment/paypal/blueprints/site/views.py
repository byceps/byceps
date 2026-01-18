"""
byceps.services.shop.payment.paypal.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2020-2026 Jan Korneffel, Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from uuid import UUID

from flask import abort, current_app, g, jsonify, request
from paypalcheckoutsdk.core import (
    LiveEnvironment,
    PayPalHttpClient,
    SandboxEnvironment,
)
from paypalcheckoutsdk.orders import OrdersGetRequest
from paypalhttp import HttpError
from paypalhttp.http_response import Result as HttpResult
from pydantic import BaseModel, ValidationError
import structlog

from byceps.config.errors import ConfigurationError
from byceps.services.shop.order import (
    order_command_service,
    order_service,
    signals as shop_order_signals,
)
from byceps.services.shop.order.email import order_email_service
from byceps.services.shop.order.models.order import Order, OrderID
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.result import Err, Ok, Result
from byceps.util.views import create_empty_json_response


log = structlog.get_logger()


blueprint = create_blueprint('shop_payment_paypal', __name__)


class CapturePayPalRequest(BaseModel):
    shop_order_id: UUID
    paypal_order_id: str


@dataclass(frozen=True, kw_only=True)
class PayPalOrderDetails:
    id: str
    transaction_id: str


@blueprint.post('/capture')
def capture_transaction():
    """Reconcile PayPal transaction."""
    if not g.user.authenticated:
        return create_empty_json_response(403)

    req = _parse_request()

    order_id = OrderID(req.shop_order_id)

    order = order_service.find_order(order_id)
    if not order or not order.is_open:
        return create_empty_json_response(400)

    try:
        paypal_result = _get_paypal_order_details(req.paypal_order_id)
    except HttpError as e:
        log.error(
            'PayPal API returned unexpected response code',
            paypal_order_id=req.paypal_order_id,
            shop_order_id=order.id,
            status_code=e.status_code,
            error_message=e.message,
        )
        return create_empty_json_response(400)

    paypal_order_details = _parse_paypal_order_details(paypal_result)

    match _check_transaction_against_order(paypal_result, order):
        case Err(errors):
            log.error(
                'PayPal order verification failed',
                paypal_order_id=req.paypal_order_id,
                shop_order_id=order.id,
                errors=errors,
            )
            return create_empty_json_response(400)

    _mark_order_as_paid(order, paypal_order_details)

    return jsonify({'status': 'OK'})


def _parse_request() -> CapturePayPalRequest:
    try:
        return CapturePayPalRequest.model_validate(request.get_json())
    except ValidationError as e:
        abort(400, e.json())


def _get_paypal_order_details(paypal_order_id: str) -> HttpResult:
    paypal_config = current_app.byceps_config.payment_gateways.paypal

    if not paypal_config:
        raise ConfigurationError('PayPal integration is not configured.')

    if not paypal_config.enabled:
        raise ConfigurationError('PayPal integration is enabled.')

    client_id = paypal_config.client_id
    client_secret = paypal_config.client_secret
    environment = paypal_config.environment

    if environment == 'live':
        environment = LiveEnvironment(
            client_id=client_id, client_secret=client_secret
        )
    else:
        environment = SandboxEnvironment(
            client_id=client_id, client_secret=client_secret
        )

    client = PayPalHttpClient(environment)

    request = OrdersGetRequest(paypal_order_id)

    return client.execute(request).result


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


def _check_transaction_against_order(
    result: HttpResult, order: Order
) -> Result[None, set[str]]:
    errors = set()

    purchase_unit = result.purchase_units[0]

    if result.status != 'COMPLETED':
        errors.add('status')

    if purchase_unit.amount.currency_code != 'EUR':
        errors.add('currency_code')

    if purchase_unit.amount.value != str(order.total_amount.amount):
        errors.add('total_amount')

    if purchase_unit.invoice_id != order.order_number:
        errors.add('invoice_id')

    if errors:
        return Err(errors)

    return Ok(None)


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

    shop_order_signals.order_paid.send(None, event=event)
