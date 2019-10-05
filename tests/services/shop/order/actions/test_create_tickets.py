"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.order import action_registry_service
from byceps.services.shop.order import event_service as order_event_service
from byceps.services.ticketing import (
    category_service as ticket_category_service,
    ticket_service,
)

from .base import OrderActionTestBase


class CreateTicketsActionTest(OrderActionTestBase):

    def setUp(self):
        super().setUp()

        self.article = self.create_article(self.shop.id, quantity=10)

        self.ticket_category = ticket_category_service.create_category(
            self.party.id, 'Deluxe'
        )

    def test_create_tickets(self):
        ticket_quantity = 4

        action_registry_service.register_tickets_creation(
            self.article.item_number, self.ticket_category.id
        )

        articles_with_quantity = [(self.article, ticket_quantity)]
        self.order = self.place_order(articles_with_quantity)

        tickets_before_paid = self.get_tickets_for_order()
        assert len(tickets_before_paid) == 0

        self.mark_order_as_paid()

        tickets_after_paid = self.get_tickets_for_order()
        assert len(tickets_after_paid) == ticket_quantity

        for ticket in tickets_after_paid:
            assert ticket.owned_by_id == self.buyer.id
            assert ticket.used_by_id == self.buyer.id

        events = order_event_service.get_events_for_order(self.order.id)
        ticket_created_events = {
            event for event in events if event.event_type == 'ticket-created'
        }
        assert len(ticket_created_events) == ticket_quantity

    # -------------------------------------------------------------------- #
    # helpers

    def get_tickets_for_order(self):
        return ticket_service.find_tickets_created_by_order(
            self.order.order_number
        )
