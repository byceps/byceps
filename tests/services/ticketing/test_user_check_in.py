"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest
from pytest import raises

from byceps.services.ticketing import (
    category_service,
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

from tests.conftest import database_recreated
from tests.helpers import create_brand, create_party, create_user


@pytest.fixture(scope='module')
def app(admin_app, db):
    with admin_app.app_context():
        with database_recreated(db):
            yield admin_app


@pytest.fixture(scope='module')
def party():
    brand = create_brand()
    return create_party(brand_id=brand.id)


@pytest.fixture(scope='module')
def category(party):
    return category_service.create_category(party.id, 'Premium')


@pytest.fixture(scope='module')
def admin(app):
    return create_user('Admin')


@pytest.fixture(scope='module')
def ticket_owner(app):
    return create_user('TicketOwner')


@pytest.fixture(scope='module')
def ticket_user(app):
    return create_user('TicketUser')


def test_check_in_user(app, db, category, admin, ticket_owner, ticket_user):
    ticket_before = create_ticket(category.id, ticket_owner.id)

    ticket_before.used_by_id = ticket_user.id
    db.session.commit()

    assert not ticket_before.user_checked_in

    events_before = event_service.get_events_for_ticket(ticket_before.id)
    assert len(events_before) == 0

    # -------------------------------- #

    ticket_id = ticket_before.id

    check_in_user(ticket_id, admin.id)

    # -------------------------------- #

    ticket_after = ticket_service.find_ticket(ticket_id)
    assert ticket_before.user_checked_in

    events_after = event_service.get_events_for_ticket(ticket_after.id)
    assert len(events_after) == 1

    ticket_revoked_event = events_after[0]
    assert ticket_revoked_event.event_type == 'user-checked-in'
    assert ticket_revoked_event.data == {
        'checked_in_user_id': str(ticket_user.id),
        'initiator_id': str(admin.id),
    }


def test_check_in_user_with_ticket_without_assigned_user(
    app, category, admin, ticket_owner
):
    ticket = create_ticket(category.id, ticket_owner.id)

    with raises(TicketLacksUser):
        check_in_user(ticket.id, admin.id)


def test_check_in_user_with_revoked_ticket(
    app, db, category, admin, ticket_owner, ticket_user
):
    ticket = create_ticket(category.id, ticket_owner.id)

    ticket.revoked = True
    ticket.used_by_id = ticket_user.id
    db.session.commit()

    with raises(TicketIsRevoked):
        check_in_user(ticket.id, admin.id)


def test_check_in_user_with_ticket_user_already_checked_in(
    app, db, category, admin, ticket_owner, ticket_user
):
    ticket = create_ticket(category.id, ticket_owner.id)

    ticket.used_by_id = ticket_user.id
    ticket.user_checked_in = True
    db.session.commit()

    with raises(UserAlreadyCheckedIn):
        check_in_user(ticket.id, admin.id)


def test_check_in_suspended_user(
    app, db, category, admin, ticket_owner, ticket_user
):
    ticket = create_ticket(category.id, ticket_owner.id)

    ticket.used_by_id = ticket_user.id
    ticket_user.suspended = True
    db.session.commit()

    with raises(UserAccountSuspended):
        check_in_user(ticket.id, admin.id)


# helpers


def create_ticket(category_id, owner_id):
    return ticket_creation_service.create_ticket(category_id, owner_id)


def check_in_user(ticket_id, admin_id):
    ticket_user_checkin_service.check_in_user(ticket_id, admin_id)
