"""
byceps.services.shop.order.order_payment_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from copy import deepcopy
from datetime import datetime
from decimal import Decimal

from sqlalchemy import delete, select

from ....database import db
from ....typing import UserID

from ...user import user_service

from .dbmodels.payment import DbPayment
from . import order_log_service
from .transfer.payment import AdditionalPaymentData, Payment
from .transfer.order import OrderID


def add_payment(
    order_id: OrderID,
    created_at: datetime,
    method: str,
    amount: Decimal,
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
        amount=db_payment.amount,
        additional_data=deepcopy(db_payment.additional_data),
    )
