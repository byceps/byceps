"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

import pytest

from byceps.database import generate_uuid7
from byceps.events.ticketing import TicketCheckedInEvent
from byceps.services.ticketing import ticket_domain_service
from byceps.services.ticketing.errors import (
    TicketBelongsToDifferentPartyError,
    TicketIsRevokedError,
    TicketLacksUserError,
    UserAccountDeletedError,
    UserAccountSuspendedError,
    UserAlreadyCheckedInError,
)
from byceps.services.ticketing.models.checkin import TicketForCheckIn
from byceps.services.ticketing.models.ticket import TicketCode, TicketID
from byceps.services.user.models.user import User
from byceps.typing import PartyID, UserID

from tests.helpers import generate_token


def test_check_in_user(party_id, build_ticket, ticket_user, initiator):
    ticket = build_ticket(party_id, used_by=ticket_user)

    actual = ticket_domain_service.check_in_user(party_id, ticket, initiator)
    assert actual.is_ok()

    check_in, event, log_entry = actual.unwrap()

    assert check_in.id is not None
    assert check_in.occurred_at is not None
    assert check_in.ticket_id == ticket.id
    assert check_in.initiator_id == initiator.id

    assert event.__class__ is TicketCheckedInEvent
    assert event.occurred_at is not None
    assert event.initiator_id == initiator.id
    assert event.initiator_screen_name == initiator.screen_name
    assert event.ticket_id == ticket.id
    assert event.ticket_code == ticket.code
    assert event.occupied_seat_id is None
    assert event.user_id == ticket_user.id
    assert event.user_screen_name == ticket_user.screen_name

    assert log_entry.id is not None
    assert log_entry.occurred_at is not None
    assert log_entry.event_type == 'user-checked-in'
    assert log_entry.ticket_id == ticket.id
    assert log_entry.data == {
        'checked_in_user_id': str(ticket_user.id),
        'initiator_id': str(initiator.id),
    }


def test_check_in_user_with_ticket_for_another_party(
    build_party_id, party_id, build_ticket, ticket_user, initiator
):
    other_party_id = build_party_id()
    ticket = build_ticket(party_id, used_by=ticket_user)

    actual = ticket_domain_service.check_in_user(
        other_party_id, ticket, initiator
    )
    assert isinstance(actual.unwrap_err(), TicketBelongsToDifferentPartyError)


def test_check_in_user_with_ticket_without_assigned_user(
    party_id, build_ticket, ticket_user, initiator
):
    ticket = build_ticket(party_id, used_by=None)

    actual = ticket_domain_service.check_in_user(party_id, ticket, initiator)
    assert isinstance(actual.unwrap_err(), TicketLacksUserError)


def test_check_in_user_with_revoked_ticket(
    party_id, build_ticket, ticket_user, initiator
):
    ticket = build_ticket(party_id, used_by=ticket_user, revoked=True)

    actual = ticket_domain_service.check_in_user(party_id, ticket, initiator)
    assert isinstance(actual.unwrap_err(), TicketIsRevokedError)


def test_check_in_user_with_ticket_user_already_checked_in(
    party_id, build_ticket, ticket_user, initiator
):
    ticket = build_ticket(party_id, used_by=ticket_user, user_checked_in=True)

    actual = ticket_domain_service.check_in_user(party_id, ticket, initiator)
    assert isinstance(actual.unwrap_err(), UserAlreadyCheckedInError)


def test_check_in_deleted_user(party_id, build_ticket, deleted_user, initiator):
    ticket = build_ticket(party_id, used_by=deleted_user)

    actual = ticket_domain_service.check_in_user(party_id, ticket, initiator)
    assert isinstance(actual.unwrap_err(), UserAccountDeletedError)


def test_check_in_suspended_user(
    party_id, build_ticket, suspended_user, initiator
):
    ticket = build_ticket(party_id, used_by=suspended_user)

    actual = ticket_domain_service.check_in_user(party_id, ticket, initiator)
    assert isinstance(actual.unwrap_err(), UserAccountSuspendedError)


# helpers


@pytest.fixture(scope='module')
def build_party_id():
    def _wrapper() -> PartyID:
        return PartyID(generate_token())

    return _wrapper


@pytest.fixture(scope='module')
def party_id(build_party_id):
    return build_party_id()


@pytest.fixture(scope='module')
def build_ticket():
    def _wrapper(
        party_id: PartyID,
        *,
        used_by: User | None = None,
        revoked: bool = False,
        user_checked_in: bool = False,
    ) -> TicketForCheckIn:
        return TicketForCheckIn(
            id=TicketID(generate_uuid7()),
            party_id=party_id,
            code=TicketCode(generate_token(5)),
            occupied_seat_id=None,
            used_by=used_by,
            revoked=revoked,
            user_checked_in=user_checked_in,
        )

    return _wrapper


@pytest.fixture(scope='module')
def build_user():
    def _wrapper(*, suspended=False, deleted=False) -> User:
        return User(
            id=UserID(generate_uuid7()),
            screen_name=None,
            suspended=suspended,
            deleted=deleted,
            locale=None,
            avatar_url=None,
        )

    return _wrapper


@pytest.fixture(scope='module')
def ticket_user(build_user):
    return build_user()


@pytest.fixture(scope='module')
def deleted_user(build_user):
    return build_user(deleted=True)


@pytest.fixture(scope='module')
def suspended_user(build_user):
    return build_user(suspended=True)


@pytest.fixture(scope='module')
def initiator(build_user):
    return build_user()
