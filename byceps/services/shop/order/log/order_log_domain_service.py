"""
byceps.services.shop.order.log.order_log_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.shop.invoice.models import Invoice
from byceps.services.shop.order.models.order import OrderID, PaymentState
from byceps.services.shop.order.models.payment import (
    AdditionalPaymentData,
    Payment,
)
from byceps.services.ticketing.models.ticket import (
    TicketBundleID,
    TicketCategoryID,
    TicketCode,
    TicketID,
)
from byceps.services.user.models.user import User, UserID
from byceps.services.user_badge.models import BadgeAwarding
from byceps.util.uuid import generate_uuid7

from .models import OrderLogEntry, OrderLogEntryData


def _build_entry(
    event_type: str,
    order_id: OrderID,
    data: OrderLogEntryData,
    *,
    occurred_at: datetime | None = None,
) -> OrderLogEntry:
    """Assemble an order log entry."""
    entry_id = generate_uuid7()

    if occurred_at is None:
        occurred_at = datetime.utcnow()

    return OrderLogEntry(
        id=entry_id,
        occurred_at=occurred_at,
        event_type=event_type,
        order_id=order_id,
        data=data,
    )


def build_order_placed_entry(
    occurred_at: datetime, order_id: OrderID, initiator: User
) -> OrderLogEntry:
    """Assemble an 'order placed' log entry."""
    data = {
        'initiator_id': str(initiator.id),
    }

    return _build_entry('order-placed', order_id, data, occurred_at=occurred_at)


def build_order_placed_confirmation_email_resent_entry(
    order_id: OrderID, initiator: User
) -> OrderLogEntry:
    """Assemble an 'order placed confirmation email resent' log entry."""
    data = {
        'initiator_id': str(initiator.id),
    }

    return _build_entry(
        'order-placed-confirmation-email-resent', order_id, data
    )


def build_orderer_updated_entry(
    order_id: OrderID,
    fields: dict[str, str],
    initiator: User,
) -> OrderLogEntry:
    """Assemble an 'orderer updated' log entry."""
    data = {
        'fields': fields,
        'initiator_id': str(initiator.id),
    }

    return _build_entry('order-orderer-updated', order_id, data)


def build_note_added_entry(
    order_id: OrderID, author: User, text: str
) -> OrderLogEntry:
    """Assemble a 'note added' log entry."""
    data = {
        'author_id': str(author.id),
        'text': text,
    }

    return _build_entry('order-note-added', order_id, data)


def build_set_shipped_flag_entry(
    order_id: OrderID, initiator: User
) -> OrderLogEntry:
    """Assemble a 'set shipped flag' log entry."""
    data = {
        'initiator_id': str(initiator.id),
    }

    return _build_entry('order-shipped', order_id, data)


def build_unset_shipped_flag_entry(
    order_id: OrderID, initiator: User
) -> OrderLogEntry:
    """Assemble an 'unset shipped flag' log entry."""
    data = {
        'initiator_id': str(initiator.id),
    }

    return _build_entry('order-shipped-withdrawn', order_id, data)


def build_payment_created_entry(
    payment: Payment, initiator: User
) -> OrderLogEntry:
    """Assemble a 'payment created' log entry."""
    data = {
        'payment_id': str(payment.id),
        'initiator_id': str(initiator.id),
    }

    return _build_entry(
        'order-payment-created',
        payment.order_id,
        data,
        occurred_at=payment.created_at,
    )


def build_order_paid_entry(
    occurred_at: datetime,
    order_id: OrderID,
    payment_state_from: PaymentState,
    payment_method: str,
    additional_payment_data: AdditionalPaymentData | None,
    initiator: User,
) -> OrderLogEntry:
    """Assemble an 'order paid' log entry."""
    data: OrderLogEntryData = {}

    # Add required, internally set properties after given additional
    # ones to ensure the former are not overridden by the latter.

    if additional_payment_data is not None:
        data.update(additional_payment_data)

    data.update(
        {
            'former_payment_state': payment_state_from.name,
            'payment_method': payment_method,
            'initiator_id': str(initiator.id),
        }
    )

    return _build_entry(
        'order-paid',
        order_id,
        data,
        occurred_at=occurred_at,
    )


def build_order_canceled_entry(
    occurred_at: datetime,
    order_id: OrderID,
    has_order_been_paid: bool,
    payment_state_from: PaymentState,
    reason: str,
    initiator: User,
) -> OrderLogEntry:
    """Assemble an 'order canceled' log entry."""
    event_type = (
        'order-canceled-after-paid'
        if has_order_been_paid
        else 'order-canceled-before-paid'
    )

    data = {
        'former_payment_state': payment_state_from.name,
        'reason': reason,
        'initiator_id': str(initiator.id),
    }

    return _build_entry(event_type, order_id, data, occurred_at=occurred_at)


def build_invoice_created_entry(
    invoice: Invoice, initiator: User
) -> OrderLogEntry:
    """Assemble an 'invoice created' log entry."""
    data = {
        'invoice_number': invoice.number,
        'initiator_id': str(initiator.id),
    }

    return _build_entry('order-invoice-created', invoice.order_id, data)


def build_ticket_created_entry(
    order_id: OrderID,
    ticket_id: TicketID,
    ticket_code: TicketCode,
    ticket_category_id: TicketCategoryID,
    ticket_owner_id: UserID,
) -> OrderLogEntry:
    """Assemble a 'ticket created' log entry."""
    data = {
        'ticket_id': str(ticket_id),
        'ticket_code': ticket_code,
        'ticket_category_id': str(ticket_category_id),
        'ticket_owner_id': str(ticket_owner_id),
    }

    return _build_entry('ticket-created', order_id, data)


def build_ticket_revoked_entry(
    order_id: OrderID,
    ticket_id: TicketID,
    ticket_code: TicketCode,
    initiator: User,
) -> OrderLogEntry:
    """Assemble a 'ticket revoked' log entry."""
    data = {
        'ticket_id': str(ticket_id),
        'ticket_code': ticket_code,
        'initiator_id': str(initiator.id),
    }

    return _build_entry('ticket-revoked', order_id, data)


def build_ticket_bundle_created_entry(
    order_id: OrderID,
    ticket_bundle_id: TicketBundleID,
    ticket_bundle_category_id: TicketCategoryID,
    ticket_bundle_ticket_quantity: int,
    ticket_bundle_owner_id: UserID,
) -> OrderLogEntry:
    """Assemble a 'ticket bundle created' log entry."""
    data = {
        'ticket_bundle_id': str(ticket_bundle_id),
        'ticket_bundle_category_id': str(ticket_bundle_category_id),
        'ticket_bundle_ticket_quantity': ticket_bundle_ticket_quantity,
        'ticket_bundle_owner_id': str(ticket_bundle_owner_id),
    }

    return _build_entry('ticket-bundle-created', order_id, data)


def build_ticket_bundle_revoked_entry(
    order_id: OrderID,
    ticket_bundle_id: TicketBundleID,
    initiator: User,
) -> OrderLogEntry:
    """Assemble a 'ticket bundle revoked' log entry."""
    data = {
        'ticket_bundle_id': str(ticket_bundle_id),
        'initiator_id': str(initiator.id),
    }

    return _build_entry('ticket-bundle-revoked', order_id, data)


def build_user_badge_awarded_entry(
    order_id: OrderID, awarding: BadgeAwarding
) -> OrderLogEntry:
    """Assemble a '(user) badge awarded' log entry."""
    data = {
        'awarding_id': str(awarding.id),
        'badge_id': str(awarding.badge_id),
        'awardee_id': str(awarding.awardee_id),
    }

    return _build_entry('badge-awarded', order_id, data)
