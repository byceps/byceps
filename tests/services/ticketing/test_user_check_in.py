"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest
from pytest import raises

from byceps.services.ticketing import (
    event_service,
    ticket_creation_service,
    ticket_service,
    ticket_user_checkin_service,
)
from byceps.services.ticketing.exceptions import (
    TicketIsRevoked,
    TicketLacksUser,
    UserAccountSuspended,
    UserAlreadyCheckedIn,
)


@pytest.fixture
def ticket(app, category, ticket_owner):
    ticket = ticket_creation_service.create_ticket(category.id, ticket_owner.id)
    yield ticket
    ticket_service.delete_ticket(ticket.id)


def test_check_in_user(app, db, ticket, ticketing_admin, ticket_user):
    ticket_before = ticket

    ticket_before.used_by_id = ticket_user.id
    db.session.commit()

    assert not ticket_before.user_checked_in

    events_before = event_service.get_events_for_ticket(ticket_before.id)
    assert len(events_before) == 0

    # -------------------------------- #

    ticket_id = ticket_before.id

    check_in_user(ticket_id, ticketing_admin.id)

    # -------------------------------- #

    ticket_after = ticket_service.find_ticket(ticket_id)
    assert ticket_before.user_checked_in

    events_after = event_service.get_events_for_ticket(ticket_after.id)
    assert len(events_after) == 1

    ticket_revoked_event = events_after[0]
    assert ticket_revoked_event.event_type == 'user-checked-in'
    assert ticket_revoked_event.data == {
        'checked_in_user_id': str(ticket_user.id),
        'initiator_id': str(ticketing_admin.id),
    }


def test_check_in_user_with_ticket_without_assigned_user(
    app, ticket, ticketing_admin
):
    with raises(TicketLacksUser):
        check_in_user(ticket.id, ticketing_admin.id)


def test_check_in_user_with_revoked_ticket(
    app, db, ticket, ticketing_admin, ticket_user
):
    ticket.revoked = True
    ticket.used_by_id = ticket_user.id
    db.session.commit()

    with raises(TicketIsRevoked):
        check_in_user(ticket.id, ticketing_admin.id)


def test_check_in_user_with_ticket_user_already_checked_in(
    app, db, ticket, ticketing_admin, ticket_user
):
    ticket.used_by_id = ticket_user.id
    ticket.user_checked_in = True
    db.session.commit()

    with raises(UserAlreadyCheckedIn):
        check_in_user(ticket.id, ticketing_admin.id)


def test_check_in_suspended_user(app, db, ticket, ticketing_admin, ticket_user):
    ticket.used_by_id = ticket_user.id
    ticket_user.suspended = True
    db.session.commit()

    with raises(UserAccountSuspended):
        check_in_user(ticket.id, ticketing_admin.id)


# helpers


def check_in_user(ticket_id, admin_id):
    ticket_user_checkin_service.check_in_user(ticket_id, admin_id)
