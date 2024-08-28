"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.database import db
from byceps.services.ticketing import (
    ticket_creation_service,
    ticket_service,
    ticket_user_checkin_service,
)


@pytest.fixture()
def ticket(admin_app, category, ticket_owner):
    return ticket_creation_service.create_ticket(category, ticket_owner)


def test_check_in_user(admin_app, party, ticket, ticketing_admin, make_user):
    ticket_user = make_user()
    initiator = ticketing_admin

    ticket_before = ticket

    ticket_before.used_by_id = ticket_user.id
    db.session.commit()

    assert not ticket_before.user_checked_in

    # -------------------------------- #

    ticket_id = ticket_before.id

    check_in_result = ticket_user_checkin_service.check_in_user(
        party.id, ticket_id, initiator
    )
    assert check_in_result.is_ok()

    check_in_result.unwrap()

    # -------------------------------- #

    ticket_after = ticket_service.get_ticket(ticket_id)
    assert ticket_after.user_checked_in

    check_in = ticket_user_checkin_service.find_check_in_for_ticket(ticket_id)
    assert check_in is not None
    assert check_in.occurred_at is not None
    assert check_in.initiator_id == initiator.id
