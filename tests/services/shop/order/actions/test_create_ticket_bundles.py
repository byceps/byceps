"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.payment import PaymentMethod
from byceps.services.shop.order import action_registry_service
from byceps.services.shop.order import event_service as order_event_service
from byceps.services.shop.order import service as order_service
from byceps.services.shop.sequence.models import Purpose
from byceps.services.shop.sequence import service as shop_sequence_service
from byceps.services.ticketing import \
    category_service as ticket_category_service, ticket_service

from testfixtures.shop_article import create_article
from testfixtures.shop_order import create_orderer

from tests.base import AbstractAppTestCase


ANY_PAYMENT_METHOD = PaymentMethod.bank_transfer


class CreateTicketBundlesActionTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

        self.admin = self.create_user_with_detail('Admin')
        self.buyer = self.create_user_with_detail('Buyer')

        shop_sequence_service.create_party_sequence(self.party.id,
            Purpose.order, prefix='article-')

        self.article = self.create_article()

        self.ticket_category = ticket_category_service.create_category(
            self.party.id, 'Deluxe')

    def test_create_ticket_bundles(self):
        ticket_quantity = 5
        bundle_quantity = 2

        action_registry_service.register_ticket_bundles_creation(
            self.article.item_number, self.ticket_category.id, ticket_quantity)

        self.order = self.create_order(bundle_quantity)

        tickets_before_paid = self.get_tickets_for_order()
        assert len(tickets_before_paid) == 0

        self.mark_order_as_paid()

        tickets_after_paid = self.get_tickets_for_order()
        assert len(tickets_after_paid) == 10

        for ticket in tickets_after_paid:
            assert ticket.owned_by_id == self.buyer.id

        events = order_event_service.get_events_for_order(self.order.id)
        ticket_bundle_created_events = {
            event for event in events
            if event.event_type == 'ticket-bundle-created'
        }
        assert len(ticket_bundle_created_events) == bundle_quantity

    # -------------------------------------------------------------------- #
    # helpers

    def create_article(self):
        article = create_article(party_id=self.party.id, quantity=10)

        self.db.session.add(article)
        self.db.session.commit()

        return article

    def create_order(self, ticket_quantity):
        orderer = create_orderer(self.buyer)

        cart = Cart()
        cart.add_item(self.article, ticket_quantity)

        return order_service.create_order(self.party.id, orderer,
            ANY_PAYMENT_METHOD, cart)

    def mark_order_as_paid(self):
        order_service.mark_order_as_paid(self.order.id, ANY_PAYMENT_METHOD,
            self.admin.id)

    def get_tickets_for_order(self):
        return ticket_service.find_tickets_created_by_order(
            self.order.order_number)
