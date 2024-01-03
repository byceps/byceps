"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.services.guest_server.models import Server, ServerID
from byceps.services.party.models import Party
from byceps.services.user.models.user import User

from tests.helpers import generate_uuid


@pytest.fixture(scope='module')
def make_server(party: Party, make_user):
    def _wrapper(
        *,
        owner: User | None = None,
        approved: bool = False,
        checked_in_at: datetime | None = None,
        checked_out_at: datetime | None = None,
    ) -> Server:
        if owner is None:
            owner = make_user()

        return Server(
            id=ServerID(generate_uuid()),
            party_id=party.id,
            created_at=datetime.utcnow(),
            creator=owner,
            owner=owner,
            description=None,
            notes_owner=None,
            notes_admin=None,
            approved=approved,
            checked_in=checked_in_at is not None,
            checked_in_at=checked_in_at,
            checked_out=checked_out_at is not None,
            checked_out_at=checked_out_at,
            addresses=set(),
        )

    return _wrapper
