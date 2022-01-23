"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.order import action_registry_service
from byceps.services.shop.order import log_service as order_log_service
from byceps.services.shop.order.transfer.order import Order
from byceps.services.ticketing import ticket_service, ticket_bundle_service

from .helpers import get_tickets_for_order, mark_order_as_paid, place_order


@pytest.fixture(scope='module')
def ticket_quantity() -> int:
    return 5


@pytest.fixture(scope='module')
def bundle_quantity() -> int:
    return 2


@pytest.fixture
def order(article, bundle_quantity, storefront, orderer) -> Order:
    articles_with_quantity = [(article, bundle_quantity)]
    return place_order(storefront.id, orderer, articles_with_quantity)


@pytest.fixture
def order_action(article, ticket_category, ticket_quantity) -> None:
    action_registry_service.register_ticket_bundles_creation(
        article.item_number, ticket_category.id, ticket_quantity
    )


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
) -> None:
    tickets_before_paid = get_tickets_for_order(order)
    assert len(tickets_before_paid) == 0

    mark_order_as_paid(order.id, admin_user.id)

    tickets_after_paid = get_tickets_for_order(order)
    assert len(tickets_after_paid) == ticket_quantity * bundle_quantity

    for ticket in tickets_after_paid:
        assert ticket.owned_by_id == orderer.user_id
        assert ticket.used_by_id == orderer.user_id

    log_entries = order_log_service.get_entries_for_order(order.id)
    ticket_bundle_created_log_entries = [
        entry
        for entry in log_entries
        if entry.event_type == 'ticket-bundle-created'
    ]
    assert len(ticket_bundle_created_log_entries) == bundle_quantity

    tear_down_bundles(tickets_after_paid)


# helpers


def tear_down_bundles(tickets) -> None:
    bundle_ids = {t.bundle_id for t in tickets}

    for ticket in tickets:
        ticket_service.delete_ticket(ticket.id)

    for bundle_id in bundle_ids:
        ticket_bundle_service.delete_bundle(bundle_id)
