"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.services.guest_server import guest_server_domain_service
from byceps.services.guest_server.errors import (
    AlreadyCheckedOutError,
    NotCheckedInError,
)


def test_check_out_server(make_server, admin_user):
    checked_in_server = make_server(
        approved=True, checked_in_at=datetime.utcnow()
    )

    assert not checked_in_server.checked_out
    assert checked_in_server.checked_out_at is None

    actual = guest_server_domain_service.check_out_server(
        checked_in_server, admin_user
    )
    assert actual.is_ok()

    checked_out_server, event = actual.unwrap()

    assert checked_out_server.checked_out
    assert checked_out_server.checked_out_at is not None

    assert event.occurred_at is not None
    assert event.initiator is not None
    assert event.initiator.id == admin_user.id
    assert event.initiator.screen_name == admin_user.screen_name
    assert event.owner.id == checked_in_server.owner.id
    assert event.owner.screen_name == checked_in_server.owner.screen_name
    assert event.server_id == checked_in_server.id


DATETIME = datetime.utcnow()


@pytest.mark.parametrize(
    ('approved', 'checked_in_at', 'checked_out_at', 'expected'),
    [
        (False, None, None, NotCheckedInError),
        (False, DATETIME, DATETIME, AlreadyCheckedOutError),
    ],
)
def test_check_out_server_error(
    make_server,
    admin_user,
    approved: bool,
    checked_in_at: datetime | None,
    checked_out_at: datetime | None,
    expected: type[AlreadyCheckedOutError | NotCheckedInError],
):
    server = make_server(
        approved=approved,
        checked_in_at=checked_in_at,
        checked_out_at=checked_out_at,
    )

    actual = guest_server_domain_service.check_out_server(server, admin_user)
    assert actual.is_err()

    err = actual.unwrap_err()
    assert isinstance(err, expected)
