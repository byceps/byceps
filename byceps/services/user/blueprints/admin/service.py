"""
byceps.services.user.blueprints.admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from collections.abc import Iterable, Iterator
from operator import attrgetter
from typing import Any
from uuid import UUID

from byceps.services.consent import consent_service, consent_subject_service
from byceps.services.newsletter import newsletter_service
from byceps.services.newsletter.models import List as NewsletterList
from byceps.services.party import party_service
from byceps.services.party.models import Party, PartyID
from byceps.services.shop.order import order_log_service, order_service
from byceps.services.site import site_service
from byceps.services.ticketing import ticket_attendance_service, ticket_service
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.user import user_log_service, user_service
from byceps.services.user.dbmodels.avatar import (
    get_absolute_url_path as get_absolute_url_path_for_avatar,
)
from byceps.services.user.models.log import UserLogEntry, UserLogEntryData
from byceps.services.user.models.user import User, UserID
from byceps.services.user_badge import user_badge_service


def get_parties_and_tickets(
    user_id: UserID,
) -> list[tuple[Party, list[DbTicket]]]:
    """Return tickets the user uses or manages, and the related parties."""
    tickets = ticket_service.get_tickets_related_to_user(user_id)

    tickets_by_party_id = _group_tickets_by_party_id(tickets)

    party_ids = set(tickets_by_party_id.keys())
    parties_by_id = _get_parties_by_id(party_ids)

    parties_and_tickets = [
        (parties_by_id[party_id], tickets)
        for party_id, tickets in tickets_by_party_id.items()
    ]

    parties_and_tickets.sort(key=lambda x: x[0].starts_at, reverse=True)

    return parties_and_tickets


def _group_tickets_by_party_id(
    tickets: Iterable[DbTicket],
) -> dict[PartyID, list[DbTicket]]:
    tickets_by_party_id: dict[PartyID, list[DbTicket]] = defaultdict(list)

    for ticket in tickets:
        tickets_by_party_id[ticket.category.party_id].append(ticket)

    return tickets_by_party_id


def _get_parties_by_id(party_ids: set[PartyID]) -> dict[PartyID, Party]:
    parties = party_service.get_parties(party_ids)
    return {p.id: p for p in parties}


def get_attended_parties(user_id: UserID) -> list[Party]:
    """Return the parties attended by the user, in order."""
    attended_parties = ticket_attendance_service.get_attended_parties(user_id)
    attended_parties.sort(key=attrgetter('starts_at'), reverse=True)
    return attended_parties


def get_newsletter_subscription_states(
    user_id: UserID,
) -> Iterator[tuple[NewsletterList, bool]]:
    lists = newsletter_service.get_all_lists()
    for list_ in lists:
        is_subscribed = newsletter_service.is_user_subscribed_to_list(
            user_id, list_.id
        )
        yield list_, is_subscribed


def get_log_entries(user_id: UserID) -> Iterator[UserLogEntryData]:
    log_entries = _collect_log_entries(user_id)

    users_by_id = _get_users_indexed_by_id(log_entries)

    for entry in log_entries:
        data = {
            'event_type': entry.event_type,
            'occurred_at': entry.occurred_at,
            'data': entry.data,
        }

        additional_data = _get_additional_data(entry, users_by_id)
        data.update(additional_data)

        yield data


def _collect_log_entries(user_id: UserID) -> list[UserLogEntry]:
    log_entries = user_log_service.get_entries_for_user(user_id)
    log_entries.extend(_fake_consent_log_entries(user_id))
    log_entries.extend(
        _fake_newsletter_subscription_update_log_entries(user_id)
    )
    log_entries.extend(_get_order_log_entries(user_id))

    return log_entries


def _fake_consent_log_entries(user_id: UserID) -> Iterator[UserLogEntry]:
    """Yield the user's consents as volatile log entries."""
    consents = consent_service.get_consents_by_user(user_id)

    subject_ids = {consent.subject_id for consent in consents}
    subjects = consent_subject_service.get_subjects(subject_ids)
    subjects_titles_by_id = {subject.id: subject.title for subject in subjects}

    for consent in consents:
        data = {
            'initiator_id': str(user_id),
            'subject_title': subjects_titles_by_id[consent.subject_id],
        }

        yield UserLogEntry(
            id=UUID('00000000-0000-0000-0000-000000000001'),
            occurred_at=consent.expressed_at,
            event_type='consent-expressed',
            user_id=user_id,
            initiator_id=user_id,
            data=data,
        )


def _fake_newsletter_subscription_update_log_entries(
    user_id: UserID,
) -> Iterator[UserLogEntry]:
    """Yield the user's newsletter subscription updates as volatile log entries."""
    lists = newsletter_service.get_all_lists()
    lists_by_id = {list_.id: list_ for list_ in lists}

    updates = newsletter_service.get_subscription_updates_for_user(user_id)

    for update in updates:
        event_type = f'newsletter-{update.state.name}'

        list_ = lists_by_id[update.list_id]

        data = {
            'list_': list_,
            'initiator_id': str(user_id),
        }

        yield UserLogEntry(
            id=UUID('00000000-0000-0000-0000-000000000001'),
            occurred_at=update.expressed_at,
            event_type=event_type,
            user_id=user_id,
            initiator_id=user_id,
            data=data,
        )


def _get_order_log_entries(initiator_id: UserID) -> Iterator[UserLogEntry]:
    """Yield orders log entries initiated by the user."""
    event_types = frozenset(
        [
            'order-canceled-after-paid',
            'order-canceled-before-paid',
            'order-paid',
            'order-placed',
        ]
    )
    log_entries = order_log_service.get_entries_by_initiator(
        initiator_id, event_types
    )

    order_ids = frozenset([entry.order_id for entry in log_entries])
    orders = order_service.get_orders(order_ids)
    orders_by_id = {order.id: order for order in orders}

    for entry in log_entries:
        order = orders_by_id[entry.order_id]
        data = {
            'initiator_id': str(initiator_id),
            'order_id': str(order.id),
            'order_number': order.order_number,
        }

        yield UserLogEntry(
            id=UUID('00000000-0000-0000-0000-000000000001'),
            occurred_at=entry.occurred_at,
            event_type=entry.event_type,
            user_id=initiator_id,
            initiator_id=initiator_id,
            data=data,
        )


def _get_users_indexed_by_id(
    log_entries: Iterable[UserLogEntry],
) -> dict[UserID, User]:
    initiator_ids = {
        _to_user_id(entry.data['initiator_id'])
        for entry in log_entries
        if 'initiator_id' in entry.data
    }

    return user_service.get_users_indexed_by_id(
        initiator_ids, include_avatars=True
    )


def _get_additional_data(
    log_entry: UserLogEntry, users_by_id: dict[UserID, User]
) -> Iterator[tuple[str, Any]]:
    if log_entry.event_type in {
        'user-avatar-removed',
        'user-avatar-updated',
        'user-created',
        'user-deleted',
        'user-details-updated',
        'user-email-address-changed',
        'user-email-address-invalidated',
        'user-initialized',
        'user-screen-name-changed',
        'user-suspended',
        'user-unsuspended',
        'password-updated',
        'consent-expressed',
        'newsletter-requested',
        'newsletter-declined',
        'order-canceled-after-paid',
        'order-canceled-before-paid',
        'order-paid',
        'order-placed',
        'orgaflag-added',
        'orgaflag-removed',
        'privacy-policy-accepted',
        'role-assigned',
        'role-deassigned',
        'user-badge-awarded',
    }:
        yield from _get_additional_data_for_user_initiated_log_entry(
            log_entry, users_by_id
        )

    if log_entry.event_type in {'user-avatar-removed', 'user-avatar-updated'}:
        url_path = get_absolute_url_path_for_avatar(log_entry.data['filename'])
        yield 'url_path', url_path

    if log_entry.event_type == 'user-badge-awarded':
        badge = user_badge_service.find_badge(log_entry.data['badge_id'])
        yield 'badge', badge

    if log_entry.event_type == 'user-details-updated':
        details = {
            k: v
            for k, v in log_entry.data.items()
            if k.startswith(('old_', 'new_'))
        }
        yield 'details', details

    if log_entry.event_type == 'user-logged-in':
        site_id = log_entry.data.get('site_id')
        if site_id:
            site = site_service.find_site(site_id)
            if site is not None:
                yield 'site', site


def _get_additional_data_for_user_initiated_log_entry(
    log_entry: UserLogEntry, users_by_id: dict[UserID, User]
) -> Iterator[tuple[str, Any]]:
    initiator_id = log_entry.initiator_id

    if initiator_id is None:
        initiator_id_str = log_entry.data.get('initiator_id')
        if initiator_id_str is not None:
            initiator_id = _to_user_id(initiator_id_str)

    if initiator_id is not None:
        yield 'initiator', users_by_id[initiator_id]


def _to_user_id(id_str: str) -> UserID:
    return UserID(UUID(id_str))
