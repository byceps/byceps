"""
byceps.services.ticketing.ticket_revocation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from ...database import db
from ...typing import UserID

from .dbmodels.log import TicketLogEntry as DbTicketLogEntry
from . import log_service, ticket_seat_management_service
from . import ticket_service
from .transfer.models import TicketID


def revoke_ticket(
    ticket_id: TicketID, initiator_id: UserID, *, reason: Optional[str] = None
) -> None:
    """Revoke the ticket."""
    ticket = ticket_service.get_ticket(ticket_id)

    # Release seat.
    if ticket.occupied_seat_id:
        ticket_seat_management_service.release_seat(ticket.id, initiator_id)

    ticket.revoked = True

    log_entry = build_ticket_revoked_log_entry(ticket.id, initiator_id, reason)
    db.session.add(log_entry)

    db.session.commit()


def revoke_tickets(
    ticket_ids: set[TicketID],
    initiator_id: UserID,
    *,
    reason: Optional[str] = None,
) -> None:
    """Revoke the tickets."""
    tickets = ticket_service.find_tickets(ticket_ids)

    # Release seats.
    for ticket in tickets:
        if ticket.occupied_seat_id:
            ticket_seat_management_service.release_seat(ticket.id, initiator_id)

    for ticket in tickets:
        ticket.revoked = True

        log_entry = build_ticket_revoked_log_entry(
            ticket.id, initiator_id, reason
        )
        db.session.add(log_entry)

    db.session.commit()


def build_ticket_revoked_log_entry(
    ticket_id: TicketID, initiator_id: UserID, reason: Optional[str] = None
) -> DbTicketLogEntry:
    data = {
        'initiator_id': str(initiator_id),
    }

    if reason:
        data['reason'] = reason

    return log_service.build_log_entry('ticket-revoked', ticket_id, data)
