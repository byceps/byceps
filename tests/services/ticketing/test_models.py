"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from uuid import UUID

import pytest

from byceps.services.ticketing.models.ticket import Ticket

from testfixtures.user import create_user


ANY_BUNDLE_ID = UUID('4138fcfb-cc18-45c0-aede-d49a8e279885')


user1 = create_user('User1')
user2 = create_user('User2')
user3 = create_user('User3')


@pytest.mark.parametrize('bundle_id, expected', [
    (ANY_BUNDLE_ID, True ),
    (None,          False),
])
def test_belongs_to_bundle(bundle_id, expected):
    ticket = create_ticket(user1.id, bundle_id=bundle_id)

    assert ticket.belongs_to_bundle == expected


@pytest.mark.parametrize('owned_by_id, seat_managed_by_id, user_managed_by_id, user_id, expected', [
    (user1.id, None    , None    , user1.id, True ),
    (user1.id, user1.id, None    , user1.id, True ),
    (user1.id, None    , user1.id, user1.id, True ),
    (user1.id, user1.id, user1.id, user1.id, True ),

    (user1.id, user2.id, None    , user1.id, True ),
    (user1.id, None    , user2.id, user1.id, True ),
    (user1.id, user2.id, user2.id, user1.id, False),  # all management rights waived

    (user2.id, None    , None    , user1.id, False),
    (user2.id, user1.id, None    , user1.id, True ),
    (user2.id, None    , user1.id, user1.id, True ),
    (user2.id, user1.id, user1.id, user1.id, True ),
])
def test_is_managed_by(
    owned_by_id, seat_managed_by_id, user_managed_by_id, user_id, expected
):
    ticket = create_ticket(owned_by_id,
                           seat_managed_by_id=seat_managed_by_id,
                           user_managed_by_id=user_managed_by_id)

    assert ticket.is_managed_by(user_id) == expected


@pytest.mark.parametrize('owned_by_id, seat_managed_by_id, user_id, expected', [
    (user1.id, None    , user1.id, True ),
    (user1.id, user1.id, user1.id, True ),

    (user1.id, None    , user1.id, True ),
    (user1.id, user2.id, user1.id, False),  # management right waived

    (user2.id, None    , user1.id, False),
    (user2.id, user1.id, user1.id, True ),
])
def test_is_seat_managed_by(owned_by_id, seat_managed_by_id, user_id, expected):
    ticket = create_ticket(owned_by_id,
                           seat_managed_by_id=seat_managed_by_id)

    assert ticket.is_seat_managed_by(user_id) == expected


@pytest.mark.parametrize('owned_by_id, user_managed_by_id, user_id, expected', [
    (user1.id, None    , user1.id, True ),
    (user1.id, user1.id, user1.id, True ),

    (user1.id, None    , user1.id, True ),
    (user1.id, user2.id, user1.id, False),  # management right waived

    (user2.id, None    , user1.id, False),
    (user2.id, user1.id, user1.id, True ),
])
def test_is_user_managed_by(owned_by_id, user_managed_by_id, user_id, expected):
    ticket = create_ticket(owned_by_id,
                           user_managed_by_id=user_managed_by_id)

    assert ticket.is_user_managed_by(user_id) == expected


def create_ticket(
    owned_by_id,
    *,
    bundle_id=None,
    seat_managed_by_id=None,
    user_managed_by_id=None,
):
    code = 'BRTZN'
    category_id = None

    ticket = Ticket(code, category_id, owned_by_id)
    ticket.bundle_id = bundle_id
    ticket.seat_managed_by_id = seat_managed_by_id
    ticket.user_managed_by_id = user_managed_by_id

    return ticket
