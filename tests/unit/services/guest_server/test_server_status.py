"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.services.guest_server.models import ServerStatus


DATETIME = datetime.utcnow()


@pytest.mark.parametrize(
    ('approved', 'checked_in_at', 'checked_out_at', 'expected'),
    [
        (False, None, None, ServerStatus.pending),
        (True, None, None, ServerStatus.approved),
        (False, DATETIME, None, ServerStatus.checked_in),
        (True, DATETIME, None, ServerStatus.checked_in),
        (False, DATETIME, DATETIME, ServerStatus.checked_out),
        (True, DATETIME, DATETIME, ServerStatus.checked_out),
    ],
)
def test_server_status(
    make_server,
    approved: bool,
    checked_in_at: datetime | None,
    checked_out_at: datetime | None,
    expected: ServerStatus,
):
    server = make_server(
        approved=approved,
        checked_in_at=checked_in_at,
        checked_out_at=checked_out_at,
    )

    assert server.status == expected
