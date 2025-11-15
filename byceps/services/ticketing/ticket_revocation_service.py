"""
byceps.services.ticketing.ticket_revocation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.database import db
from byceps.services.user.models.user import User

from . import ticket_log_service, ticket_seat_management_service, ticket_service
from .models.log import TicketLogEntry
from .models.ticket import TicketID


def revoke_ticket(
    ticket_id: TicketID, initiator: User, *, reason: str | None = None
) -> None:
    """Revoke the ticket."""
    db_ticket = ticket_service.get_ticket(ticket_id)

    # Release seat.
    if db_ticket.occupied_seat_id:
        ticket_seat_management_service.release_seat(
            db_ticket.id, initiator
        ).unwrap()

    db_ticket.revoked = True

    log_entry = build_ticket_revoked_log_entry(db_ticket.id, initiator, reason)
    db_log_entry = ticket_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()


def revoke_tickets(
    ticket_ids: set[TicketID],
    initiator: User,
    *,
    reason: str | None = None,
) -> None:
    """Revoke the tickets."""
    db_tickets = ticket_service.get_tickets(ticket_ids)

    # Release seats.
    for db_ticket in db_tickets:
        if db_ticket.occupied_seat_id:
            ticket_seat_management_service.release_seat(
                db_ticket.id, initiator
            ).unwrap()

    for db_ticket in db_tickets:
        db_ticket.revoked = True

        log_entry = build_ticket_revoked_log_entry(
            db_ticket.id, initiator, reason
        )
        db_log_entry = ticket_log_service.to_db_entry(log_entry)
        db.session.add(db_log_entry)

    db.session.commit()


def build_ticket_revoked_log_entry(
    ticket_id: TicketID, initiator: User, reason: str | None = None
) -> TicketLogEntry:
    data = {
        'initiator_id': str(initiator.id),
    }

    if reason:
        data['reason'] = reason

    return ticket_log_service.build_entry('ticket-revoked', ticket_id, data)
