"""
byceps.services.shop.order.order_log_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.ticketing.models.ticket import (
    TicketBundleID,
    TicketCategoryID,
    TicketCode,
    TicketID,
)
from byceps.services.user.models.user import User, UserID
from byceps.services.user_badge.models import BadgeAwarding
from byceps.util.uuid import generate_uuid7

from .models.log import OrderLogEntry, OrderLogEntryData
from .models.order import OrderID


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
