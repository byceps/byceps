"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest
from pytest import raises

from byceps.database import db
from byceps.events.ticketing import TicketCheckedIn
from byceps.services.ticketing import (
    event_service,
    ticket_creation_service,
    ticket_service,
    ticket_user_checkin_service,
)
from byceps.services.ticketing.exceptions import (
    TicketBelongsToDifferentParty,
    TicketIsRevoked,
    TicketLacksUser,
    UserAccountSuspended,
    UserAlreadyCheckedIn,
)

from tests.helpers import create_party


@pytest.fixture
def ticket(admin_app, category, ticket_owner):
    ticket = ticket_creation_service.create_ticket(
        category.party_id, category.id, ticket_owner.id
    )
    yield ticket
    ticket_service.delete_ticket(ticket.id)


def test_check_in_user(admin_app, party, ticket, ticketing_admin, make_user):
    ticket_user = make_user()

    ticket_before = ticket

    ticket_before.used_by_id = ticket_user.id
    db.session.commit()

    assert not ticket_before.user_checked_in

    events_before = event_service.get_events_for_ticket(ticket_before.id)
    assert len(events_before) == 0

    # -------------------------------- #

    ticket_id = ticket_before.id

    event = check_in_user(party.id, ticket_id, ticketing_admin.id)

    # -------------------------------- #

    ticket_after = ticket_service.get_ticket(ticket_id)
    assert ticket_after.user_checked_in

    assert event.__class__ is TicketCheckedIn
    assert event.occurred_at is not None
    assert event.initiator_id == ticketing_admin.id
    assert event.initiator_screen_name == ticketing_admin.screen_name
    assert event.ticket_id == ticket.id
    assert event.ticket_code == ticket.code
    assert event.occupied_seat_id is None
    assert event.user_id == ticket_user.id
    assert event.user_screen_name == ticket_user.screen_name

    ticket_events_after = event_service.get_events_for_ticket(ticket_after.id)
    assert len(ticket_events_after) == 1

    ticket_checked_in_event = ticket_events_after[0]
    assert ticket_checked_in_event.event_type == 'user-checked-in'
    assert ticket_checked_in_event.data == {
        'checked_in_user_id': str(ticket_user.id),
        'initiator_id': str(ticketing_admin.id),
    }


def test_check_in_user_with_ticket_for_another_party(
    admin_app, brand, ticket, ticketing_admin
):
    other_party = create_party(brand.id, 'next-party', 'Next Party')

    with raises(TicketBelongsToDifferentParty):
        check_in_user(other_party.id, ticket.id, ticketing_admin.id)


def test_check_in_user_with_ticket_without_assigned_user(
    admin_app, party, ticket, ticketing_admin
):
    with raises(TicketLacksUser):
        check_in_user(party.id, ticket.id, ticketing_admin.id)


def test_check_in_user_with_revoked_ticket(
    admin_app, party, ticket, ticketing_admin, make_user
):
    ticket_user = make_user()

    ticket.revoked = True
    ticket.used_by_id = ticket_user.id
    db.session.commit()

    with raises(TicketIsRevoked):
        check_in_user(party.id, ticket.id, ticketing_admin.id)


def test_check_in_user_with_ticket_user_already_checked_in(
    admin_app, party, ticket, ticketing_admin, make_user
):
    ticket_user = make_user()

    ticket.used_by_id = ticket_user.id
    ticket.user_checked_in = True
    db.session.commit()

    with raises(UserAlreadyCheckedIn):
        check_in_user(party.id, ticket.id, ticketing_admin.id)


def test_check_in_suspended_user(
    admin_app, party, ticket, ticketing_admin, make_user
):
    ticket_user = make_user(suspended=True)

    ticket.used_by_id = ticket_user.id
    db.session.commit()

    with raises(UserAccountSuspended):
        check_in_user(party.id, ticket.id, ticketing_admin.id)


# helpers


def check_in_user(party_id, ticket_id, admin_id):
    return ticket_user_checkin_service.check_in_user(
        party_id, ticket_id, admin_id
    )
