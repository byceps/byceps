# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from nose2.tools import params

from byceps.blueprints.ticket.models import Ticket

from testfixtures.user import create_user


user1 = create_user(1)
user2 = create_user(2)
user3 = create_user(3)


@params(
    (user1, None,  None,  user1, True ),
    (user1, user1, None,  user1, True ),
    (user1, None,  user1, user1, True ),
    (user1, user1, user1, user1, True ),

    (user1, user2, None,  user1, True ),
    (user1, None,  user2, user1, True ),
    (user1, user2, user2, user1, False),  # all management rights waived

    (user2, None,  None,  user1, False),
    (user2, user1, None,  user1, True ),
    (user2, None,  user1, user1, True ),
    (user2, user1, user1, user1, True ),
)
def test_is_managed_by(owned_by, seat_managed_by, user_managed_by, user, expected):
    ticket = create_ticket(owned_by,
                           seat_managed_by=seat_managed_by,
                           user_managed_by=user_managed_by)

    assert ticket.is_managed_by(user) == expected


@params(
    (user1, None,  user1, True ),
    (user1, user1, user1, True ),

    (user1, None,  user1, True ),
    (user1, user2, user1, False),  # management right waived

    (user2, None,  user1, False),
    (user2, user1, user1, True ),
)
def test_is_seat_managed_by(owned_by, seat_managed_by, user, expected):
    ticket = create_ticket(owned_by,
                           seat_managed_by=seat_managed_by)

    assert ticket.is_seat_managed_by(user) == expected


@params(
    (user1, None,  user1, True ),
    (user1, user1, user1, True ),

    (user1, None,  user1, True ),
    (user1, user2, user1, False),  # management right waived

    (user2, None,  user1, False),
    (user2, user1, user1, True ),
)
def test_is_user_managed_by(owned_by, user_managed_by, user, expected):
    ticket = create_ticket(owned_by,
                           user_managed_by=user_managed_by)

    assert ticket.is_user_managed_by(user) == expected


def create_ticket(owned_by, *, seat_managed_by=None, user_managed_by=None):
    category = None
    ticket = Ticket(category, owned_by)
    ticket.seat_managed_by = seat_managed_by
    ticket.user_managed_by = user_managed_by
    return ticket
