"""
byceps.services.shop.order.order_payment_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from copy import deepcopy
from datetime import datetime

from flask_babel import format_currency
from moneyed import Money
from sqlalchemy import delete, select

from ....database import db
from ....typing import UserID
from ....util.templating import load_template

from ...snippet.models import SnippetScope
from ...snippet import snippet_service
from ...user import user_service

from .dbmodels.payment import DbPayment
from .models.payment import AdditionalPaymentData, Payment
from .models.order import Order, OrderID
from . import order_log_service


def add_payment(
    order_id: OrderID,
    created_at: datetime,
    method: str,
    amount: Money,
    initiator_id: UserID,
    additional_data: AdditionalPaymentData,
) -> Payment:
    """Add a payment to an order."""
    initiator = user_service.get_user(initiator_id)

    db_payment = DbPayment(
        order_id, created_at, method, amount, additional_data
    )
    db.session.add(db_payment)
    db.session.commit()

    payment = _db_entity_to_payment(db_payment)

    log_entry_data = {
        'initiator_id': str(initiator.id),
        'payment_id': str(payment.id),
    }
    order_log_service.create_entry(
        'order-payment-created', payment.order_id, log_entry_data
    )

    return payment


def delete_payments_for_order(order_id: OrderID) -> None:
    """Delete all payments that belong to the order."""
    db.session.execute(delete(DbPayment).where(DbPayment.order_id == order_id))
    db.session.commit()


def get_payments_for_order(order_id: OrderID) -> list[Payment]:
    """Return the payments for that order."""
    db_payments = db.session.scalars(
        select(DbPayment).filter_by(order_id=order_id)
    ).all()

    return [_db_entity_to_payment(db_payment) for db_payment in db_payments]


def _db_entity_to_payment(db_payment: DbPayment) -> Payment:
    return Payment(
        id=db_payment.id,
        order_id=db_payment.order_id,
        created_at=db_payment.created_at,
        method=db_payment.method,
        amount=Money(db_payment.amount, db_payment.currency),
        additional_data=deepcopy(db_payment.additional_data),
    )


def get_email_payment_instructions(order: Order, language_code: str) -> str:
    """Return the email payment instructions for that order and language.

    Raise error if not found.
    """
    scope = SnippetScope('shop', str(order.shop_id))
    snippet_content = snippet_service.get_snippet_body(
        scope, 'email_payment_instructions', language_code
    )

    template = load_template(snippet_content)
    return template.render(
        order_id=order.id,
        order_number=order.order_number,
    )


def get_html_payment_instructions(order: Order, language_code: str) -> str:
    """Return the HTML payment instructions for that order and language.

    Raise error if not found.
    """
    scope = SnippetScope('shop', str(order.shop_id))
    snippet_content = snippet_service.get_snippet_body(
        scope, 'payment_instructions', language_code
    )

    template = load_template(snippet_content)
    return template.render(
        order_number=order.order_number,
        total_amount=format_currency(
            order.total_amount.amount, order.total_amount.currency.code
        ),
    )
