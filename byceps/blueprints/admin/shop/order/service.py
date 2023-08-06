"""
byceps.blueprints.admin.shop.order.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable, Iterator
from uuid import UUID

from byceps.services.shop.cancelation_request import cancelation_request_service
from byceps.services.shop.order import order_log_service, order_service
from byceps.services.shop.order.models.log import (
    OrderLogEntry,
    OrderLogEntryData,
)
from byceps.services.shop.order.models.order import OrderID
from byceps.services.ticketing import ticket_category_service
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.services.user_badge import user_badge_service


def get_enriched_log_entry_data_for_order(
    order_id: OrderID,
) -> list[OrderLogEntryData]:
    log_entries = order_log_service.get_entries_for_order(order_id)
    log_entries.extend(_fake_cancelation_request_log_entries(order_id))
    return list(enrich_log_entry_data(log_entries))


def _fake_cancelation_request_log_entries(
    order_id: OrderID,
) -> Iterator[OrderLogEntry]:
    """Yield cancelation requests for the order as volatile log entries."""
    order = order_service.get_order(order_id)

    cancelation_request = (
        cancelation_request_service.get_request_for_order_number(
            order.order_number
        )
    )
    if cancelation_request is None:
        return

    data = {
        'initiator_id': str(order.placed_by.id),
    }

    yield OrderLogEntry(
        id=UUID('00000000-0000-0000-0000-000000000001'),
        occurred_at=cancelation_request.created_at,
        event_type='order-cancelation-requested',
        order_id=order.id,
        data=data,
    )


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

    awardee_id = log_entry.data['awardee_id']
    awardee = user_service.get_user(awardee_id, include_avatar=True)

    return {
        'badge_label': badge.label,
        'awardee': awardee,
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
    _owner_id = log_entry.data[
        'ticket_bundle_owner_id'
    ]  # Available, but currently not used.

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
    _category_id = log_entry.data[
        'ticket_category_id'
    ]  # Available, but currently not used.
    _owner_id = log_entry.data[
        'ticket_owner_id'
    ]  # Available, but currently not used.

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
