"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.seating import area_service, category_service, seat_service
from byceps.services.ticketing import ticket_service

from testfixtures.user import create_user

from tests.base import AbstractAppTestCase


class TicketAssignmentServiceTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.owner = self.create_user('Ticket_Owner')

        self.category = self.create_category('Premium')

        self.ticket = ticket_service.create_ticket(self.category.id,
                                                   self.owner.id)

    def test_appoint_and_withdraw_user_manager(self):
        manager = self.create_user('Ticket_Manager')

        self.assertIsNone(self.ticket.user_managed_by_id)

        ticket_service.appoint_user_manager(self.ticket.id, manager.id)
        self.assertEqual(self.ticket.user_managed_by_id, manager.id)

        ticket_service.withdraw_user_manager(self.ticket.id)
        self.assertIsNone(self.ticket.user_managed_by_id)

    def test_appoint_and_withdraw_user(self):
        user = self.create_user('Ticket_User')

        self.assertIsNone(self.ticket.used_by_id)

        ticket_service.appoint_user(self.ticket.id, user.id)
        self.assertEqual(self.ticket.used_by_id, user.id)

        ticket_service.withdraw_user(self.ticket.id)
        self.assertIsNone(self.ticket.used_by_id)

    def test_appoint_and_withdraw_seat_manager(self):
        manager = self.create_user('Ticket_Manager')

        self.assertIsNone(self.ticket.seat_managed_by_id)

        ticket_service.appoint_seat_manager(self.ticket.id, manager.id)
        self.assertEqual(self.ticket.seat_managed_by_id, manager.id)

        ticket_service.withdraw_seat_manager(self.ticket.id)
        self.assertIsNone(self.ticket.seat_managed_by_id)

    def test_occupy_and_release_seat(self):
        area = self.create_area('main', 'Main Hall')
        seat = seat_service.create_seat(area, 0, 0, self.category)

        self.assertIsNone(self.ticket.occupied_seat_id)

        ticket_service.occupy_seat(self.ticket.id, seat.id)
        self.assertEqual(self.ticket.occupied_seat_id, seat.id)

        ticket_service.release_seat(self.ticket.id)
        self.assertIsNone(self.ticket.occupied_seat_id)

    # -------------------------------------------------------------------- #
    # helpers

    def create_user(self, screen_name):
        user = create_user(screen_name)

        self.db.session.add(user)
        self.db.session.commit()

        return user

    def create_area(self, slug, title):
        return area_service.create_area(self.party.id, slug, title)

    def create_category(self, title):
        return category_service.create_category(self.party.id, title)
