"""
byceps.blueprints.admin.shop.order.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
import dataclasses
from typing import Iterable, Iterator, Sequence

from .....services.shop.article import service as article_service
from .....services.shop.article.transfer.models import Article, ArticleNumber
from .....services.shop.order import (
    log_service as order_log_service,
    service as order_service,
)
from .....services.shop.order.transfer.log import (
    OrderLogEntry,
    OrderLogEntryData,
)
from .....services.shop.order.transfer.order import Order, OrderID
from .....services.ticketing import category_service as ticket_category_service
from .....services.user.dbmodels.user import User as DbUser
from .....services.user import service as user_service
from .....services.user.transfer.models import User
from .....services.user_badge import badge_service as user_badge_service


@dataclass(frozen=True)
class OrderWithOrderer(Order):
    placed_by: DbUser


def extend_order_tuples_with_orderer(
    orders: Sequence[Order],
) -> Iterator[OrderWithOrderer]:
    orderer_ids = {order.placed_by_id for order in orders}
    orderers = user_service.get_users(orderer_ids, include_avatars=True)
    orderers_by_id = user_service.index_users_by_id(orderers)

    for order in orders:
        orderer = orderers_by_id[order.placed_by_id]
        values = dataclasses.astuple(order) + (orderer,)
        yield OrderWithOrderer(*values)


def get_articles_by_item_number(order: Order) -> dict[ArticleNumber, Article]:
    numbers = {line_item.article_number for line_item in order.line_items}

    articles = article_service.get_articles_by_numbers(numbers)

    return {article.item_number: article for article in articles}


def get_enriched_log_entry_data_for_order(
    order_id: OrderID,
) -> list[OrderLogEntryData]:
    log_entries = order_log_service.get_entries_for_order(order_id)
    return list(enrich_log_entry_data(log_entries))


def enrich_log_entry_data(
    log_entries: Iterable[OrderLogEntry],
) -> Iterator[OrderLogEntryData]:
    order_ids = frozenset([entry.order_id for entry in log_entries])
    orders = order_service.get_orders(order_ids)
    orders_by_id = {order.id: order for order in orders}

    user_ids = {
        entry.data['initiator_id']
        for entry in log_entries
        if 'initiator_id' in entry.data
    }
    users = user_service.get_users(user_ids, include_avatars=True)
    users_by_id = {str(user.id): user for user in users}

    for entry in log_entries:
        order = orders_by_id[entry.order_id]

        data = {
            'event_type': entry.event_type,
            'occurred_at': entry.occurred_at,
            'order_id': str(order.id),
            'order_number': order.order_number,
            'data': entry.data,
        }

        additional_data = _get_additional_data(entry, users_by_id)
        data.update(additional_data)

        yield data


def _get_additional_data(
    log_entry: OrderLogEntry, users_by_id: dict[str, User]
) -> OrderLogEntryData:
    if log_entry.event_type == 'badge-awarded':
        return _get_additional_data_for_badge_awarded(log_entry)
    elif log_entry.event_type == 'order-invoice-created':
        return {}
    elif log_entry.event_type == 'order-note-added':
        return _get_additional_data_for_order_note_added(log_entry)
    elif log_entry.event_type == 'ticket-bundle-created':
        return _get_additional_data_for_ticket_bundle_created(log_entry)
    elif log_entry.event_type == 'ticket-bundle-revoked':
        return _get_additional_data_for_ticket_bundle_revoked(
            log_entry, users_by_id
        )
    elif log_entry.event_type == 'ticket-created':
        return _get_additional_data_for_ticket_created(log_entry)
    elif log_entry.event_type == 'ticket-revoked':
        return _get_additional_data_for_ticket_revoked(log_entry, users_by_id)
    else:
        return _get_additional_data_for_standard_log_entry(
            log_entry, users_by_id
        )


def _get_additional_data_for_standard_log_entry(
    log_entry: OrderLogEntry, users_by_id: dict[str, User]
) -> OrderLogEntryData:
    initiator_id = log_entry.data['initiator_id']

    return {
        'initiator': users_by_id[initiator_id],
    }


def _get_additional_data_for_badge_awarded(
    log_entry: OrderLogEntry,
) -> OrderLogEntryData:
    badge_id = log_entry.data['badge_id']
    badge = user_badge_service.get_badge(badge_id)

    recipient_id = log_entry.data['recipient_id']
    recipient = user_service.get_user(recipient_id, include_avatar=True)

    return {
        'badge_label': badge.label,
        'recipient': recipient,
    }


def _get_additional_data_for_order_note_added(
    log_entry: OrderLogEntry,
) -> OrderLogEntryData:
    author_id = log_entry.data['author_id']
    author = user_service.get_user(author_id, include_avatar=True)

    return {
        'author': author,
    }


def _get_additional_data_for_ticket_bundle_created(
    log_entry: OrderLogEntry,
) -> OrderLogEntryData:
    bundle_id = log_entry.data['ticket_bundle_id']
    category_id = log_entry.data['ticket_bundle_category_id']
    ticket_quantity = log_entry.data['ticket_bundle_ticket_quantity']
    owner_id = log_entry.data['ticket_bundle_owner_id']

    category = ticket_category_service.find_category(category_id)
    category_title = category.title if (category is not None) else None

    return {
        'bundle_id': bundle_id,
        'ticket_category_title': category_title,
        'ticket_quantity': ticket_quantity,
    }


def _get_additional_data_for_ticket_bundle_revoked(
    log_entry: OrderLogEntry, users_by_id: dict[str, User]
) -> OrderLogEntryData:
    bundle_id = log_entry.data['ticket_bundle_id']

    data = {
        'bundle_id': bundle_id,
    }

    initiator_id = log_entry.data.get('initiator_id')
    if initiator_id:
        data['initiator'] = users_by_id[initiator_id]

    return data


def _get_additional_data_for_ticket_created(
    log_entry: OrderLogEntry,
) -> OrderLogEntryData:
    ticket_id = log_entry.data['ticket_id']
    ticket_code = log_entry.data['ticket_code']
    category_id = log_entry.data['ticket_category_id']
    owner_id = log_entry.data['ticket_owner_id']

    return {
        'ticket_id': ticket_id,
        'ticket_code': ticket_code,
    }


def _get_additional_data_for_ticket_revoked(
    log_entry: OrderLogEntry, users_by_id: dict[str, User]
) -> OrderLogEntryData:
    ticket_id = log_entry.data['ticket_id']
    ticket_code = log_entry.data['ticket_code']

    data = {
        'ticket_id': ticket_id,
        'ticket_code': ticket_code,
    }

    initiator_id = log_entry.data.get('initiator_id')
    if initiator_id:
        data['initiator'] = users_by_id[initiator_id]

    return data
