"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.shop.order import action_service, action_registry_service
from byceps.services.shop.order import event_service as order_event_service
from byceps.services.shop.order import service as order_service
from byceps.services.ticketing import ticket_service, ticket_bundle_service

from .helpers import get_tickets_for_order, mark_order_as_paid, place_order


@pytest.fixture(scope='module')
def ticket_quantity():
    return 5


@pytest.fixture(scope='module')
def bundle_quantity():
    return 2


@pytest.fixture
def order(article, bundle_quantity, storefront, orderer):
    articles_with_quantity = [(article, bundle_quantity)]
    order = place_order(storefront.id, orderer, articles_with_quantity)

    yield order

    order_service.delete_order(order.id)


@pytest.fixture
def order_action(article, ticket_category, ticket_quantity):
    action_registry_service.register_ticket_bundles_creation(
        article.item_number, ticket_category.id, ticket_quantity
    )

    yield

    action_service.delete_actions(article.item_number)


def test_create_ticket_bundles(
    admin_app,
    article,
    ticket_category,
    ticket_quantity,
    bundle_quantity,
    admin_user,
    orderer,
    order,
    order_action,
):
    tickets_before_paid = get_tickets_for_order(order)
    assert len(tickets_before_paid) == 0

    mark_order_as_paid(order.id, admin_user.id)

    tickets_after_paid = get_tickets_for_order(order)
    assert len(tickets_after_paid) == ticket_quantity * bundle_quantity

    for ticket in tickets_after_paid:
        assert ticket.owned_by_id == orderer.user_id
        assert ticket.used_by_id == orderer.user_id

    events = order_event_service.get_events_for_order(order.id)
    ticket_bundle_created_events = {
        event
        for event in events
        if event.event_type == 'ticket-bundle-created'
    }
    assert len(ticket_bundle_created_events) == bundle_quantity

    tear_down_bundles(tickets_after_paid)


# helpers


def tear_down_bundles(tickets):
    bundle_ids = {t.bundle_id for t in tickets}

    for ticket in tickets:
        ticket_service.delete_ticket(ticket.id)

    for bundle_id in bundle_ids:
        ticket_bundle_service.delete_bundle(bundle_id)
