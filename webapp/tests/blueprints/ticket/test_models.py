# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest import TestCase

from nose2.tools import params

from byceps.blueprints.ticket.models import Ticket

from testfixtures.user import create_user


user1 = create_user(1)
user2 = create_user(2)
user3 = create_user(3)


class TicketTestCase(TestCase):

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
    def test_is_managed_by(self, owned_by, seat_managed_by, user_managed_by, user, expected):
        ticket = create_ticket(owned_by,
                               seat_managed_by=seat_managed_by,
                               user_managed_by=user_managed_by)

        actual = ticket.is_managed_by(user)

        self.assertEquals(actual, expected)

    @params(
        (user1, None,  user1, True ),
        (user1, user1, user1, True ),

        (user1, None,  user1, True ),
        (user1, user2, user1, False),  # management right waived

        (user2, None,  user1, False),
        (user2, user1, user1, True ),
    )
    def test_is_seat_managed_by(self, owned_by, seat_managed_by, user, expected):
        ticket = create_ticket(owned_by,
                               seat_managed_by=seat_managed_by)

        actual = ticket.is_seat_managed_by(user)

        self.assertEquals(actual, expected)

    @params(
        (user1, None,  user1, True ),
        (user1, user1, user1, True ),

        (user1, None,  user1, True ),
        (user1, user2, user1, False),  # management right waived

        (user2, None,  user1, False),
        (user2, user1, user1, True ),
    )
    def test_is_user_managed_by(self, owned_by, user_managed_by, user, expected):
        ticket = create_ticket(owned_by,
                               user_managed_by=user_managed_by)

        actual = ticket.is_user_managed_by(user)

        self.assertEquals(actual, expected)


def create_ticket(owned_by, *, seat_managed_by=None, user_managed_by=None):
    category = None
    ticket = Ticket(category, owned_by)
    ticket.seat_managed_by = seat_managed_by
    ticket.user_managed_by = user_managed_by
    return ticket
