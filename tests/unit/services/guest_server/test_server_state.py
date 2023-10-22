"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

import pytest

from byceps.services.guest_server.models import ServerState


DATETIME = datetime.utcnow()


@pytest.mark.parametrize(
    ('approved', 'checked_in_at', 'checked_out_at', 'expected'),
    [
        (False, None, None, ServerState.pending),
        (True, None, None, ServerState.approved),
        (False, DATETIME, None, ServerState.checked_in),
        (True, DATETIME, None, ServerState.checked_in),
        (False, DATETIME, DATETIME, ServerState.checked_out),
        (True, DATETIME, DATETIME, ServerState.checked_out),
    ],
)
def test_server_status(
    make_server,
    approved: bool,
    checked_in_at: datetime | None,
    checked_out_at: datetime | None,
    expected: ServerState,
):
    server = make_server(
        approved=approved,
        checked_in_at=checked_in_at,
        checked_out_at=checked_out_at,
    )

    assert server.state == expected
