"""
byceps.services.shop.payment.stripe.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2020-2026 Jan Korneffel, Micha Ober, Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from flask import abort, g, jsonify, make_response, request, url_for
from moneyed import Money
from pydantic import BaseModel, ValidationError
import stripe
import structlog

from byceps.byceps_app import get_current_byceps_app
from byceps.config.errors import ConfigurationError
from byceps.config.models import StripeConfig
from byceps.services.shop.order import (
    order_command_service,
    order_service,
    signals as shop_order_signals,
)
from byceps.services.shop.order.email import order_email_service
from byceps.services.shop.order.models.order import OrderID
from byceps.services.user import user_service
from byceps.services.user.models import UserID
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.views import create_empty_json_response


log = structlog.get_logger()


blueprint = create_blueprint('shop_payment_stripe', __name__)


class CreatePaymentIntent(BaseModel):
    shop_order_id: UUID


@blueprint.post('/create_checkout_session')
def create_checkout_session():
    if not g.user.authenticated:
        return create_empty_json_response(403)

    req = _parse_request()

    order_id = OrderID(req.shop_order_id)

    order = order_service.find_order(order_id)
    if not order or not order.is_open:
        return jsonify(error='Order does not exist or is not open'), 400

    session = _build_checkout_session(order, g.user.id)

    return jsonify(id=session.id)


def _build_checkout_session(order, user_id: UserID):
    line_items = _build_line_items(order)

    email_address = user_service.get_email_address(user_id)

    redirect_url = url_for(
        'shop_orders.view', order_id=order.id, _external=True
    )

    metadata = {
        'shop_order_id': str(order.id),
        'order_number': order.order_number,
    }

    stripe.api_key = _get_enabled_stripe_configuration().secret_key
    stripe.api_version = '2022-11-15'

    session = stripe.checkout.Session.create(
        customer_email=email_address,
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=redirect_url,
        cancel_url=redirect_url,
        metadata=metadata,
        idempotency_key=str(order.id),
    )

    return session


def _build_line_items(order):
    line_items = [
        {
            'price_data': {
                'currency': _get_currency_code(line_item.unit_price),
                'product_data': {
                    'name': line_item.name,
                },
                'unit_amount': int(line_item.unit_price.amount.shift(2)),
            },
            'quantity': line_item.quantity,
        }
        for line_item in order.line_items
    ]

    return line_items


@blueprint.post('/webhook')
def event_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = _get_enabled_stripe_configuration().webhook_secret

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )

    except ValueError:
        log.error('Invalid payload')
        return create_empty_json_response(400)

    except stripe.error.SignatureVerificationError:
        log.error('Invalid signature')
        return create_empty_json_response(400)

    if event.type == 'checkout.session.completed':
        checkout_session = event.data.object
        _fulfill_order(checkout_session)

        return create_empty_json_response(200)
    else:
        log.error('Unsupported event type: %s', event.type)

    # Return error response by default
    return create_empty_json_response(400)


def _fulfill_order(session: stripe.checkout.Session):
    session_id = session.id

    shop_order_id = session.metadata.get('shop_order_id')
    if shop_order_id is None:
        log.error(
            'Error processing checkout session: '
            'shop_order_id not found in metadata.',
            session_id=session_id,
        )
        return

    order = order_service.find_order(shop_order_id)

    if not order or not order.is_open:
        log.error(
            'Error processing checkout session: '
            'Order does not exist or is not open.',
            session_id=session_id,
            shop_order_id=shop_order_id,
        )
        return

    if not _check_transaction_against_order(session, order):
        log.error(
            'Error processing checkout session: Verification for order failed.',
            session_id=session_id,
            shop_order_id=shop_order_id,
        )
        return

    paid_order, event = order_command_service.mark_order_as_paid(
        order.id,
        'stripe',
        order.placed_by,
        additional_payment_data={
            'stripe_session_id': session_id,
            'stripe_payment_id': session.payment_intent,
        },
    ).unwrap()

    order_email_service.send_email_for_paid_order_to_orderer(paid_order)

    shop_order_signals.order_paid.send(None, event=event)


def _check_transaction_against_order(session, order):
    return (
        session.payment_status == 'paid'
        and session.currency == _get_currency_code(order.total_amount)
        and session.amount_total == int(order.total_amount.amount.shift(2))
        and session.metadata['order_number'] == order.order_number
    )


def _parse_request() -> CreatePaymentIntent:
    try:
        return CreatePaymentIntent.model_validate(request.get_json())
    except ValidationError as e:
        abort(make_response(jsonify(error=str(e)), 400))


def _get_currency_code(money: Money) -> str:
    return money.currency.code.lower()


def _get_enabled_stripe_configuration() -> StripeConfig:
    payment_gateways_config = (
        get_current_byceps_app().byceps_config.payment_gateways
    )

    stripe_config = (
        payment_gateways_config.stripe if payment_gateways_config else None
    )

    if not stripe_config:
        raise ConfigurationError('Stripe integration is not configured.')

    if not stripe_config.enabled:
        raise ConfigurationError('Stripe integration is not enabled.')

    return stripe_config
