"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.database import db
from byceps.events.ticketing import TicketCheckedInEvent
from byceps.services.ticketing import (
    ticket_creation_service,
    ticket_log_service,
    ticket_service,
    ticket_user_checkin_service,
)
from byceps.services.ticketing.errors import (
    TicketBelongsToDifferentPartyError,
    TicketIsRevokedError,
    TicketLacksUserError,
    UserAccountSuspendedError,
    UserAlreadyCheckedInError,
)


@pytest.fixture()
def ticket(admin_app, category, ticket_owner):
    return ticket_creation_service.create_ticket(
        category.party_id, category.id, ticket_owner.id
    )


def test_check_in_user(admin_app, party, ticket, ticketing_admin, make_user):
    ticket_user = make_user()
    initiator = ticketing_admin

    ticket_before = ticket

    ticket_before.used_by_id = ticket_user.id
    db.session.commit()

    assert not ticket_before.user_checked_in

    log_entries_before = ticket_log_service.get_entries_for_ticket(
        ticket_before.id
    )
    assert len(log_entries_before) == 0

    # -------------------------------- #

    ticket_id = ticket_before.id

    check_in_result = check_in_user(party.id, ticket_id, initiator.id)
    assert check_in_result.is_ok()

    event = check_in_result.unwrap()

    # -------------------------------- #

    ticket_after = ticket_service.get_ticket(ticket_id)
    assert ticket_after.user_checked_in

    assert event.__class__ is TicketCheckedInEvent
    assert event.occurred_at is not None
    assert event.initiator_id == initiator.id
    assert event.initiator_screen_name == initiator.screen_name
    assert event.ticket_id == ticket.id
    assert event.ticket_code == ticket.code
    assert event.occupied_seat_id is None
    assert event.user_id == ticket_user.id
    assert event.user_screen_name == ticket_user.screen_name

    check_in = ticket_user_checkin_service.find_check_in_for_ticket(ticket_id)
    assert check_in is not None
    assert check_in.occurred_at is not None
    assert check_in.initiator_id == initiator.id

    log_entries_after = ticket_log_service.get_entries_for_ticket(
        ticket_after.id
    )
    assert len(log_entries_after) == 1

    ticket_checked_in_log_entry = log_entries_after[0]
    assert ticket_checked_in_log_entry.event_type == 'user-checked-in'
    assert ticket_checked_in_log_entry.data == {
        'checked_in_user_id': str(ticket_user.id),
        'initiator_id': str(initiator.id),
    }


def test_check_in_user_with_ticket_for_another_party(
    admin_app, brand, make_party, ticket, ticketing_admin
):
    other_party = make_party(brand.id)

    actual = check_in_user(other_party.id, ticket.id, ticketing_admin.id)
    assert isinstance(actual.unwrap_err(), TicketBelongsToDifferentPartyError)


def test_check_in_user_with_ticket_without_assigned_user(
    admin_app, party, ticket, ticketing_admin
):
    actual = check_in_user(party.id, ticket.id, ticketing_admin.id)
    assert isinstance(actual.unwrap_err(), TicketLacksUserError)


def test_check_in_user_with_revoked_ticket(
    admin_app, party, ticket, ticketing_admin, make_user
):
    ticket_user = make_user()

    ticket.revoked = True
    ticket.used_by_id = ticket_user.id
    db.session.commit()

    actual = check_in_user(party.id, ticket.id, ticketing_admin.id)
    assert isinstance(actual.unwrap_err(), TicketIsRevokedError)


def test_check_in_user_with_ticket_user_already_checked_in(
    admin_app, party, ticket, ticketing_admin, make_user
):
    ticket_user = make_user()

    ticket.used_by_id = ticket_user.id
    ticket.user_checked_in = True
    db.session.commit()

    actual = check_in_user(party.id, ticket.id, ticketing_admin.id)
    assert isinstance(actual.unwrap_err(), UserAlreadyCheckedInError)


def test_check_in_suspended_user(
    admin_app, party, ticket, ticketing_admin, make_user
):
    ticket_user = make_user(suspended=True)

    ticket.used_by_id = ticket_user.id
    db.session.commit()

    actual = check_in_user(party.id, ticket.id, ticketing_admin.id)
    assert isinstance(actual.unwrap_err(), UserAccountSuspendedError)


# helpers


def check_in_user(party_id, ticket_id, admin_id):
    return ticket_user_checkin_service.check_in_user(
        party_id, ticket_id, admin_id
    )
