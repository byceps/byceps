"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.ticketing import category_service, event_service, \
    ticket_service

from tests.base import AbstractAppTestCase


class TicketRevocationTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

        self.category_id = self.create_category('Premium').id
        self.owner_id = self.create_user('Ticket_Owner').id

    def test_revoke_ticket(self):
        ticket_before = ticket_service.create_ticket(self.category_id, self.owner_id)
        assert not ticket_before.revoked

        events_before = event_service.get_events_for_ticket(ticket_before.id)
        assert len(events_before) == 0

        # -------------------------------- #

        ticket_id = ticket_before.id

        ticket_service.revoke_ticket(ticket_id)

        # -------------------------------- #

        ticket_after = ticket_service.find_ticket(ticket_id)
        assert ticket_after.revoked

        events_after = event_service.get_events_for_ticket(ticket_after.id)
        assert len(events_after) == 1

        ticket_revoked_event = events_after[0]
        assert ticket_revoked_event.event_type == 'ticket-revoked'
        assert ticket_revoked_event.data == {}

    def test_revoke_tickets(self):
        tickets_before = ticket_service.create_tickets(self.category_id, self.owner_id, 3)
        for ticket_before in tickets_before:
            assert not ticket_before.revoked

            events_before = event_service.get_events_for_ticket(ticket_before.id)
            assert len(events_before) == 0

        # -------------------------------- #

        ticket_ids = {ticket.id for ticket in tickets_before}

        ticket_service.revoke_tickets(ticket_ids)

        # -------------------------------- #

        tickets_after = ticket_service.find_tickets(ticket_ids)
        for ticket_after in tickets_after:
            assert ticket_after.revoked

            events_after = event_service.get_events_for_ticket(ticket_after.id)
            assert len(events_after) == 1

            ticket_revoked_event = events_after[0]
            assert ticket_revoked_event.event_type == 'ticket-revoked'
            assert ticket_revoked_event.data == {}

    # -------------------------------------------------------------------- #
    # helpers

    def create_category(self, title):
        return category_service.create_category(self.party.id, title)
