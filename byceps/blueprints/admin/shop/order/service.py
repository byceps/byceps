"""
byceps.blueprints.admin.shop.order.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
import dataclasses
from typing import Iterator, Sequence

from .....services.shop.article import service as article_service
from .....services.shop.article.transfer.models import Article, ArticleNumber
from .....services.shop.order.dbmodels.order_event import (
    OrderEvent,
    OrderEventData,
)
from .....services.shop.order import event_service as order_event_service
from .....services.shop.order import service as order_service
from .....services.shop.order.transfer.models import Order, OrderID
from .....services.ticketing import category_service as ticket_category_service
from .....services.user.dbmodels.user import User as DbUser
from .....services.user import service as user_service
from .....services.user.transfer.models import User
from .....services.user_badge import badge_service as user_badge_service
from .....typing import UserID


@dataclass(frozen=True)
class OrderWithOrderer(Order):
    placed_by: DbUser


def extend_order_tuples_with_orderer(
    orders: Sequence[Order],
) -> Iterator[OrderWithOrderer]:
    orderer_ids = {order.placed_by_id for order in orders}
    orderers = user_service.find_users(orderer_ids, include_avatars=True)
    orderers_by_id = user_service.index_users_by_id(orderers)

    for order in orders:
        orderer = orderers_by_id[order.placed_by_id]
        values = dataclasses.astuple(order) + (orderer,)
        yield OrderWithOrderer(*values)


def get_articles_by_item_number(order: Order) -> dict[ArticleNumber, Article]:
    numbers = {item.article_number for item in order.items}

    articles = article_service.get_articles_by_numbers(numbers)

    return {article.item_number: article for article in articles}


def get_events(order_id: OrderID) -> Iterator[OrderEventData]:
    events = order_event_service.get_events_for_order(order_id)
    events.insert(0, _fake_order_placement_event(order_id))

    user_ids = {
        event.data['initiator_id']
        for event in events
        if 'initiator_id' in event.data
    }
    users = user_service.find_users(user_ids, include_avatars=True)
    users_by_id = {str(user.id): user for user in users}

    for event in events:
        data = {
            'event': event.event_type,
            'occurred_at': event.occurred_at,
            'data': event.data,
        }

        additional_data = _get_additional_data(event, users_by_id)
        data.update(additional_data)

        yield data


def _fake_order_placement_event(order_id: OrderID) -> OrderEvent:
    order = order_service.find_order_with_details(order_id)
    if order is None:
        raise ValueError('Unknown order ID')

    data = {
        'initiator_id': str(order.placed_by_id),
    }

    return OrderEvent(order.created_at, 'order-placed', order.id, data)


def _get_additional_data(
    event: OrderEvent, users_by_id: dict[UserID, User]
) -> OrderEventData:
    if event.event_type == 'badge-awarded':
        return _get_additional_data_for_badge_awarded(event)
    elif event.event_type == 'order-note-added':
        return _get_additional_data_for_order_note_added(event)
    elif event.event_type == 'ticket-bundle-created':
        return _get_additional_data_for_ticket_bundle_created(event)
    elif event.event_type == 'ticket-bundle-revoked':
        return _get_additional_data_for_ticket_bundle_revoked(
            event, users_by_id
        )
    elif event.event_type == 'ticket-created':
        return _get_additional_data_for_ticket_created(event)
    elif event.event_type == 'ticket-revoked':
        return _get_additional_data_for_ticket_revoked(event, users_by_id)
    else:
        return _get_additional_data_for_standard_event(event, users_by_id)


def _get_additional_data_for_standard_event(
    event: OrderEvent, users_by_id: dict[UserID, User]
) -> OrderEventData:
    initiator_id = event.data['initiator_id']

    return {
        'initiator': users_by_id[initiator_id],
    }


def _get_additional_data_for_badge_awarded(event: OrderEvent) -> OrderEventData:
    badge_id = event.data['badge_id']
    badge = user_badge_service.get_badge(badge_id)

    recipient_id = event.data['recipient_id']
    recipient = user_service.get_user(recipient_id)

    return {
        'badge_label': badge.label,
        'recipient': recipient,
    }


def _get_additional_data_for_order_note_added(event: OrderEvent) -> OrderEventData:
    author_id = event.data['author_id']
    author = user_service.get_user(author_id)

    return {
        'author': author,
    }


def _get_additional_data_for_ticket_bundle_created(
    event: OrderEvent,
) -> OrderEventData:
    bundle_id = event.data['ticket_bundle_id']
    category_id = event.data['ticket_bundle_category_id']
    ticket_quantity = event.data['ticket_bundle_ticket_quantity']
    owner_id = event.data['ticket_bundle_owner_id']

    category = ticket_category_service.find_category(category_id)
    category_title = category.title if (category is not None) else None

    return {
        'bundle_id': bundle_id,
        'ticket_category_title': category_title,
        'ticket_quantity': ticket_quantity,
    }


def _get_additional_data_for_ticket_bundle_revoked(
    event: OrderEvent, users_by_id: dict[UserID, User]
) -> OrderEventData:
    bundle_id = event.data['ticket_bundle_id']

    data = {
        'bundle_id': bundle_id,
    }

    initiator_id = event.data.get('initiator_id')
    if initiator_id:
        data['initiator'] = users_by_id[initiator_id]

    return data


def _get_additional_data_for_ticket_created(
    event: OrderEvent,
) -> OrderEventData:
    ticket_id = event.data['ticket_id']
    ticket_code = event.data['ticket_code']
    category_id = event.data['ticket_category_id']
    owner_id = event.data['ticket_owner_id']

    return {
        'ticket_id': ticket_id,
        'ticket_code': ticket_code,
    }


def _get_additional_data_for_ticket_revoked(
    event: OrderEvent, users_by_id: dict[UserID, User]
) -> OrderEventData:
    ticket_id = event.data['ticket_id']
    ticket_code = event.data['ticket_code']

    data = {
        'ticket_code': ticket_code,
    }

    initiator_id = event.data.get('initiator_id')
    if initiator_id:
        data['initiator'] = users_by_id[initiator_id]

    return data
