"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pytest import raises

from byceps.services.ticketing import category_service, event_service, \
    ticket_service
from byceps.services.ticketing.ticket_service import TicketIsRevoked, \
    TicketLacksUser, UserAlreadyCheckIn

from tests.base import AbstractAppTestCase


class UserCheckInTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

        self.category_id = self.create_category('Premium').id
        self.orga_id = self.create_user('Party_Orga').id
        self.owner_id = self.create_user('Ticket_Owner').id
        self.user_id = self.create_user('Ticket_User').id

    def test_check_in_user(self):
        ticket_before = ticket_service.create_ticket(self.category_id, self.owner_id)

        ticket_before.used_by_id = self.user_id
        self.db.session.commit()

        assert not ticket_before.user_checked_in

        events_before = event_service.get_events_for_ticket(ticket_before.id)
        assert len(events_before) == 0

        # -------------------------------- #

        ticket_id = ticket_before.id

        ticket_service.check_in_user(ticket_id, self.orga_id)

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

    def test_check_in_user_with_revoked_ticket(self):
        ticket = ticket_service.create_ticket(self.category_id, self.owner_id)

        ticket.revoked = True
        ticket.used_by_id = self.user_id
        self.db.session.commit()

        with raises(TicketIsRevoked):
            ticket_service.check_in_user(ticket.id, self.orga_id)

    def test_check_in_user_with_ticket_user_already_checked_in(self):
        ticket = ticket_service.create_ticket(self.category_id, self.owner_id)

        ticket.used_by_id = self.user_id
        ticket.user_checked_in = True
        self.db.session.commit()

        with raises(UserAlreadyCheckIn):
            ticket_service.check_in_user(ticket.id, self.orga_id)

    # -------------------------------------------------------------------- #
    # helpers

    def create_category(self, title):
        return category_service.create_category(self.party.id, title)
