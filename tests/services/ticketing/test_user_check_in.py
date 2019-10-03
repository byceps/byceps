"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pytest import raises

from byceps.services.ticketing import (
    category_service,
    event_service,
    ticket_creation_service,
    ticket_service,
    ticket_user_checkin_service,
)
from byceps.services.ticketing.exceptions import (
    TicketIsRevoked,
    TicketLacksUser,
    UserAccountSuspended,
    UserAlreadyCheckedIn,
)

from tests.base import AbstractAppTestCase
from tests.helpers import create_brand, create_party, create_user


class UserCheckInTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        brand = create_brand()
        self.party = create_party(brand_id=brand.id)

        self.category_id = self.create_category('Premium').id
        self.orga_id = create_user('Party_Orga').id
        self.owner_id = create_user('Ticket_Owner').id
        self.user = create_user('Ticket_User')
        self.user_id = self.user.id

    def test_check_in_user(self):
        ticket_before = create_ticket(self.category_id, self.owner_id)

        ticket_before.used_by_id = self.user_id
        self.db.session.commit()

        assert not ticket_before.user_checked_in

        events_before = event_service.get_events_for_ticket(ticket_before.id)
        assert len(events_before) == 0

        # -------------------------------- #

        ticket_id = ticket_before.id

        self.check_in_user(ticket_id)

        # -------------------------------- #

        ticket_after = ticket_service.find_ticket(ticket_id)
        assert ticket_before.user_checked_in

        events_after = event_service.get_events_for_ticket(ticket_after.id)
        assert len(events_after) == 1

        ticket_revoked_event = events_after[0]
        assert ticket_revoked_event.event_type == 'user-checked-in'
        assert ticket_revoked_event.data == {
            'checked_in_user_id': str(self.user_id),
            'initiator_id': str(self.orga_id),
        }

    def test_check_in_user_with_ticket_without_assigned_user(self):
        ticket = create_ticket(self.category_id, self.owner_id)

        with raises(TicketLacksUser):
            self.check_in_user(ticket.id)

    def test_check_in_user_with_revoked_ticket(self):
        ticket = create_ticket(self.category_id, self.owner_id)

        ticket.revoked = True
        ticket.used_by_id = self.user_id
        self.db.session.commit()

        with raises(TicketIsRevoked):
            self.check_in_user(ticket.id)

    def test_check_in_user_with_ticket_user_already_checked_in(self):
        ticket = create_ticket(self.category_id, self.owner_id)

        ticket.used_by_id = self.user_id
        ticket.user_checked_in = True
        self.db.session.commit()

        with raises(UserAlreadyCheckedIn):
            self.check_in_user(ticket.id)

    def test_check_in_suspended_user(self):
        ticket = create_ticket(self.category_id, self.owner_id)

        ticket.used_by_id = self.user_id
        self.user.suspended = True
        self.db.session.commit()

        with raises(UserAccountSuspended):
            self.check_in_user(ticket.id)

    # -------------------------------------------------------------------- #
    # helpers

    def create_category(self, title):
        return category_service.create_category(self.party.id, title)

    def check_in_user(self, ticket_id):
        ticket_user_checkin_service.check_in_user(ticket_id, self.orga_id)


def create_ticket(category_id, owner_id):
    return ticket_creation_service.create_ticket(category_id, owner_id)
