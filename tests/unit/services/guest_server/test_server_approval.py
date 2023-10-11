"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from byceps.services.guest_server import guest_server_domain_service
from byceps.services.guest_server.errors import AlreadyApprovedError


def test_approved_server(make_server, admin_user):
    pending_server = make_server(approved=False)

    assert not pending_server.approved

    actual = guest_server_domain_service.approve_server(
        pending_server, admin_user
    )
    assert actual.is_ok()

    approved_server, event = actual.unwrap()

    assert approved_server.approved

    assert event.occurred_at is not None
    assert event.initiator_id == admin_user.id
    assert event.initiator_screen_name == admin_user.screen_name
    assert event.owner_id == pending_server.owner.id
    assert event.owner_screen_name == pending_server.owner.screen_name
    assert event.server_id == pending_server.id


def test_approved_server_error(make_server, admin_user):
    server = make_server(approved=True)

    actual = guest_server_domain_service.approve_server(server, admin_user)
    assert actual.is_err()

    err = actual.unwrap_err()
    assert isinstance(err, AlreadyApprovedError)
