"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

import pytest

from byceps.services.party.models import PartyID
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing.models.ticket import (
    TicketCategory,
    TicketCategoryID,
    TicketID,
)

from tests.helpers import generate_uuid


ANY_BUNDLE_ID = UUID('4138fcfb-cc18-45c0-aede-d49a8e279885')

user_id1 = UUID('388925a8-1f67-4506-9dde-63a9880139a6')
user_id2 = UUID('cd9685fe-b503-41ce-a6e5-5a4762c29cbc')


@pytest.mark.parametrize(
    ('bundle_id', 'expected'),
    [
        (ANY_BUNDLE_ID, True),
        (None, False),
    ],
)
def test_belongs_to_bundle(bundle_id, expected):
    ticket = create_ticket(user_id1, bundle_id=bundle_id)

    assert ticket.belongs_to_bundle == expected


# fmt: off
@pytest.mark.parametrize(
    (
        'owned_by_id',
        'seat_managed_by_id',
        'user_managed_by_id',
        'user_id',
        'expected',
    ),
    [
        (user_id1, None    , None    , user_id1, True ),
        (user_id1, user_id1, None    , user_id1, True ),
        (user_id1, None    , user_id1, user_id1, True ),
        (user_id1, user_id1, user_id1, user_id1, True ),

        (user_id1, user_id2, None    , user_id1, True ),
        (user_id1, None    , user_id2, user_id1, True ),
        (user_id1, user_id2, user_id2, user_id1, False),  # all management rights waived

        (user_id2, None    , None    , user_id1, False),
        (user_id2, user_id1, None    , user_id1, True ),
        (user_id2, None    , user_id1, user_id1, True ),
        (user_id2, user_id1, user_id1, user_id1, True ),
    ],
)
# fmt: on
def test_is_managed_by(
    owned_by_id, seat_managed_by_id, user_managed_by_id, user_id, expected
):
    ticket = create_ticket(
        owned_by_id,
        seat_managed_by_id=seat_managed_by_id,
        user_managed_by_id=user_managed_by_id,
    )

    assert ticket.is_managed_by(user_id) == expected


# fmt: off
@pytest.mark.parametrize(
    ('owned_by_id', 'seat_managed_by_id', 'user_id', 'expected'),
    [
        (user_id1, None    , user_id1, True ),
        (user_id1, user_id1, user_id1, True ),

        (user_id1, None    , user_id1, True ),
        (user_id1, user_id2, user_id1, False),  # management right waived

        (user_id2, None    , user_id1, False),
        (user_id2, user_id1, user_id1, True ),
    ],
)
# fmt: on
def test_is_seat_managed_by(owned_by_id, seat_managed_by_id, user_id, expected):
    ticket = create_ticket(owned_by_id, seat_managed_by_id=seat_managed_by_id)

    assert ticket.is_seat_managed_by(user_id) == expected


# fmt: off
@pytest.mark.parametrize(
    ('owned_by_id', 'user_managed_by_id', 'user_id', 'expected'),
    [
        (user_id1, None    , user_id1, True ),
        (user_id1, user_id1, user_id1, True ),

        (user_id1, None    , user_id1, True ),
        (user_id1, user_id2, user_id1, False),  # management right waived

        (user_id2, None    , user_id1, False),
        (user_id2, user_id1, user_id1, True ),
    ],
)
# fmt: on
def test_is_user_managed_by(owned_by_id, user_managed_by_id, user_id, expected):
    ticket = create_ticket(owned_by_id, user_managed_by_id=user_managed_by_id)

    assert ticket.is_user_managed_by(user_id) == expected


def create_ticket(
    owned_by_id,
    *,
    bundle_id=None,
    seat_managed_by_id=None,
    user_managed_by_id=None,
):
    ticket_id = TicketID(generate_uuid())
    created_at = datetime.utcnow()
    category = TicketCategory(
        id=TicketCategoryID(generate_uuid()),
        party_id=PartyID('megacon-99'),
        title='Standard',
    )
    code = 'BRTZN'

    ticket = DbTicket(
        ticket_id, created_at, category, code, owned_by_id, bundle_id=bundle_id
    )
    ticket.seat_managed_by_id = seat_managed_by_id
    ticket.user_managed_by_id = user_managed_by_id

    return ticket
