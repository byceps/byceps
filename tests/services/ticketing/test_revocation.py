"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.seating import category_service
from byceps.services.ticketing import ticket_service

from tests.base import AbstractAppTestCase


class TicketRevocationTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

        self.category_id = self.create_category('Premium').id
        self.owner_id = self.create_user('Ticket_Owner').id

    def test_revoke_ticket(self):
        ticket_before = ticket_service.create_ticket(self.category_id, self.owner_id)
        self.assertNotRevoked(ticket_before)

        ticket_id = ticket_before.id

        ticket_service.revoke_ticket(ticket_id)

        ticket_after = ticket_service.find_ticket(ticket_id)
        self.assertRevoked(ticket_after)

    def test_revoke_tickets(self):
        tickets_before = ticket_service.create_tickets(self.category_id, self.owner_id, 3)
        for ticket in tickets_before:
            self.assertNotRevoked(ticket)

        ticket_ids = {ticket.id for ticket in tickets_before}

        ticket_service.revoke_tickets(ticket_ids)

        tickets_after = ticket_service.find_tickets(ticket_ids)
        for ticket in tickets_after:
            self.assertRevoked(ticket)

    # -------------------------------------------------------------------- #
    # helpers

    def create_category(self, title):
        return category_service.create_category(self.party.id, title)

    def assertNotRevoked(self, ticket):
        self.assertFalse(ticket.revoked)

    def assertRevoked(self, ticket):
        self.assertTrue(ticket.revoked)
