"""
byceps.blueprints.admin.user.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from collections import defaultdict
from operator import attrgetter
from typing import Any, Iterator, Sequence

from ....services.consent import consent_service, subject_service
from ....services.newsletter import service as newsletter_service
from ....services.newsletter.transfer.models import List as NewsletterList
from ....services.party import service as party_service
from ....services.party.transfer.models import Party
from ....services.shop.order import event_service as order_event_service
from ....services.shop.order import service as order_service
from ....services.site import service as site_service
from ....services.ticketing.dbmodels.ticket import Ticket as DbTicket
from ....services.ticketing import attendance_service, ticket_service
from ....services.user import event_service
from ....services.user.dbmodels.event import (
    UserEvent as DbUserEvent,
    UserEventData,
)
from ....services.user import service as user_service
from ....services.user.transfer.models import User
from ....services.user_avatar import service as avatar_service
from ....services.user_badge import badge_service as user_badge_service
from ....typing import PartyID, UserID


def get_parties_and_tickets(
    user_id: UserID,
) -> list[tuple[Party, list[DbTicket]]]:
    """Return tickets the user uses or manages, and the related parties."""
    tickets = ticket_service.find_tickets_related_to_user(user_id)

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
    tickets: Sequence[DbTicket],
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
    attended_parties = attendance_service.get_attended_parties(user_id)
    attended_parties.sort(key=attrgetter('starts_at'), reverse=True)
    return attended_parties


def get_newsletter_subscription_states(
    user_id: UserID,
) -> Iterator[tuple[NewsletterList, bool]]:
    lists = newsletter_service.get_all_lists()
    for list_ in lists:
        is_subscribed = newsletter_service.is_subscribed(user_id, list_.id)
        yield list_, is_subscribed


def get_events(user_id: UserID) -> Iterator[UserEventData]:
    events = event_service.get_events_for_user(user_id)
    events.extend(_fake_avatar_update_events(user_id))
    events.extend(_fake_consent_events(user_id))
    events.extend(_fake_newsletter_subscription_update_events(user_id))
    events.extend(_get_order_events(user_id))

    user_ids = {
        event.data['initiator_id']
        for event in events
        if 'initiator_id' in event.data
    }
    users = user_service.get_users(user_ids, include_avatars=True)
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


def _fake_avatar_update_events(user_id: UserID) -> Iterator[DbUserEvent]:
    """Yield the user's avatar updates as volatile events."""
    avatar_updates = avatar_service.get_avatars_uploaded_by_user(user_id)

    for avatar_update in avatar_updates:
        data = {
            'initiator_id': str(user_id),
            'url_path': avatar_update.url_path,
        }

        yield DbUserEvent(
            avatar_update.occurred_at, 'user-avatar-updated', user_id, data
        )


def _fake_consent_events(user_id: UserID) -> Iterator[DbUserEvent]:
    """Yield the user's consents as volatile events."""
    consents = consent_service.get_consents_by_user(user_id)

    subject_ids = {consent.subject_id for consent in consents}
    subjects = subject_service.get_subjects(subject_ids)
    subjects_titles_by_id = {subject.id: subject.title for subject in subjects}

    for consent in consents:
        data = {
            'initiator_id': str(user_id),
            'subject_title': subjects_titles_by_id[consent.subject_id],
        }

        yield DbUserEvent(
            consent.expressed_at, 'consent-expressed', user_id, data
        )


def _fake_newsletter_subscription_update_events(
    user_id: UserID,
) -> Iterator[DbUserEvent]:
    """Yield the user's newsletter subscription updates as volatile events."""
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

        yield DbUserEvent(update.expressed_at, event_type, user_id, data)


def _get_order_events(initiator_id: UserID) -> Iterator[DbUserEvent]:
    """Yield orders events initiated by the user."""
    event_types = frozenset(
        [
            'order-placed',
        ]
    )
    events = order_event_service.get_events_of_types_by_initiator(
        event_types, initiator_id
    )

    order_ids = frozenset([event.order_id for event in events])
    orders = order_service.get_orders(order_ids)
    orders_by_id = {order.id: order for order in orders}

    for event in events:
        order = orders_by_id[event.order_id]
        data = {
            'initiator_id': str(initiator_id),
            'order_id': str(order.id),
            'order_number': order.order_number,
        }

        yield DbUserEvent(
            event.occurred_at, event.event_type, initiator_id, data
        )


def _get_additional_data(
    event: DbUserEvent, users_by_id: dict[str, User]
) -> Iterator[tuple[str, Any]]:
    if event.event_type in {
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
        'user-avatar-updated',
        'consent-expressed',
        'newsletter-requested',
        'newsletter-declined',
        'order-placed',
        'orgaflag-added',
        'orgaflag-removed',
        'privacy-policy-accepted',
        'role-assigned',
        'role-deassigned',
        'user-badge-awarded',
    }:
        yield from _get_additional_data_for_user_initiated_event(
            event, users_by_id
        )

    if event.event_type == 'user-badge-awarded':
        badge = user_badge_service.find_badge(event.data['badge_id'])
        yield 'badge', badge

    if event.event_type == 'user-details-updated':
        details = {
            k: v
            for k, v in event.data.items()
            if k.startswith('old_') or k.startswith('new_')
        }
        yield 'details', details

    if event.event_type in {'user-created', 'user-logged-in'}:
        site_id = event.data.get('site_id')
        if site_id:
            site = site_service.find_site(site_id)
            if site is not None:
                yield 'site', site


def _get_additional_data_for_user_initiated_event(
    event: DbUserEvent, users_by_id: dict[str, User]
) -> Iterator[tuple[str, Any]]:
    initiator_id = event.data.get('initiator_id')
    if initiator_id is not None:
        yield 'initiator', users_by_id[initiator_id]
