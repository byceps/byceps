"""
byceps.blueprints.admin.user.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from datetime import datetime, timedelta
from operator import attrgetter
from typing import Any, Dict, Iterator, List, Optional, Sequence, Set, Tuple

from ....database import db, paginate, Pagination
from ....services.consent import consent_service
from ....services.newsletter import service as newsletter_service
from ....services.newsletter.transfer.models import List as NewsletterList
from ....services.party import service as party_service
from ....services.party.transfer.models import Party
from ....services.shop.order import service as order_service
from ....services.ticketing.models.ticket import Ticket as DbTicket
from ....services.ticketing import attendance_service, ticket_service
from ....services.user import event_service
from ....services.user.models.detail import UserDetail as DbUserDetail
from ....services.user.models.event import (
    UserEvent as DbUserEvent,
    UserEventData,
)
from ....services.user.models.user import User as DbUser
from ....services.user import service as user_service
from ....services.user.transfer.models import User
from ....services.user_avatar import service as avatar_service
from ....services.user_badge import badge_service as user_badge_service
from ....typing import PartyID, UserID

from .models import Detail, UserStateFilter, UserWithCreationDetails


def get_users_paginated(
    page, per_page, *, search_term=None, state_filter=None
) -> Pagination:
    """Return the users to show on the specified page, optionally
    filtered by search term or flags.
    """
    query = DbUser.query \
        .options(
            db.joinedload('avatar_selection').joinedload('avatar'),
            db.joinedload('detail').load_only('first_names', 'last_name'),
        ) \
        .order_by(DbUser.created_at.desc())

    query = _filter_by_state(query, state_filter)

    if search_term:
        query = _filter_by_search_term(query, search_term)

    return paginate(
        query,
        page,
        per_page,
        item_mapper=_db_entity_to_user_with_creation_details,
    )


def _filter_by_state(query, state_filter):
    if state_filter == UserStateFilter.active:
        return query \
            .filter_by(initialized=True) \
            .filter_by(suspended=False) \
            .filter_by(deleted=False)
    elif state_filter == UserStateFilter.uninitialized:
        return query \
            .filter_by(initialized=False) \
            .filter_by(suspended=False) \
            .filter_by(deleted=False)
    elif state_filter == UserStateFilter.suspended:
        return query \
            .filter_by(suspended=True) \
            .filter_by(deleted=False)
    elif state_filter == UserStateFilter.deleted:
        return query \
            .filter_by(deleted=True)
    else:
        return query


def _filter_by_search_term(query, search_term):
    ilike_pattern = f'%{search_term}%'

    return query \
        .join(DbUserDetail) \
        .filter(
            db.or_(
                DbUser.email_address.ilike(ilike_pattern),
                DbUser.screen_name.ilike(ilike_pattern),
                DbUserDetail.first_names.ilike(ilike_pattern),
                DbUserDetail.last_name.ilike(ilike_pattern)
            )
        )


def get_users_created_since(
    delta: timedelta, limit: Optional[int] = None
) -> List[User]:
    """Return the user accounts created since `delta` ago."""
    filter_starts_at = datetime.utcnow() - delta

    query = DbUser.query \
        .options(
            db.joinedload('avatar_selection').joinedload('avatar'),
            db.joinedload('detail').load_only('first_names', 'last_name'),
        ) \
        .filter(DbUser.created_at >= filter_starts_at) \
        .order_by(DbUser.created_at.desc())

    if limit is not None:
        query = query.limit(limit)

    users = query.all()

    return [_db_entity_to_user_with_creation_details(u) for u in users]


def _db_entity_to_user_with_creation_details(
    user: DbUser,
) -> UserWithCreationDetails:
    is_orga = False  # Not interesting here.
    full_name = user.detail.full_name if user.detail is not None else None
    detail = Detail(full_name)

    return UserWithCreationDetails(
        user.id,
        user.screen_name,
        user.suspended,
        user.deleted,
        user.avatar.url if user.avatar else None,
        is_orga,
        user.created_at,
        user.initialized,
        detail,
    )


def get_parties_and_tickets(
    user_id: UserID,
) -> List[Tuple[Party, List[DbTicket]]]:
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
) -> Dict[PartyID, List[DbTicket]]:
    tickets_by_party_id: Dict[PartyID, List[DbTicket]] = defaultdict(list)

    for ticket in tickets:
        tickets_by_party_id[ticket.category.party_id].append(ticket)

    return tickets_by_party_id


def _get_parties_by_id(party_ids: Set[PartyID]) -> Dict[PartyID, Party]:
    parties = party_service.get_parties(party_ids)
    return {p.id: p for p in parties}


def get_attended_parties(user_id: UserID) -> List[Party]:
    """Return the parties attended by the user, in order."""
    attended_parties = attendance_service.get_attended_parties(user_id)
    attended_parties.sort(key=attrgetter('starts_at'), reverse=True)
    return attended_parties


def get_newsletter_subscriptions(
    user_id: UserID,
) -> Iterator[Tuple[NewsletterList, bool]]:
    lists = newsletter_service.get_all_lists()
    for list_ in lists:
        is_subscribed = newsletter_service.is_subscribed(user_id, list_.id)
        yield list_, is_subscribed


def get_events(user_id: UserID) -> Iterator[UserEventData]:
    events = event_service.get_events_for_user(user_id)
    events.extend(_fake_avatar_update_events(user_id))
    events.extend(_fake_consent_events(user_id))
    events.extend(_fake_newsletter_subscription_update_events(user_id))
    events.extend(_fake_order_events(user_id))

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

    for consent in consents:
        data = {
            'initiator_id': str(user_id),
            'subject_title': consent.subject.title,
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


def _fake_order_events(user_id: UserID) -> Iterator[DbUserEvent]:
    """Yield the orders placed by the user as volatile events."""
    orders = order_service.get_orders_placed_by_user(user_id)

    for order in orders:
        data = {
            'initiator_id': str(user_id),
            'order': order,
        }

        yield DbUserEvent(order.created_at, 'order-placed', user_id, data)


def _get_additional_data(
    event: DbUserEvent, users_by_id: Dict[str, User]
) -> Iterator[Tuple[str, Any]]:
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


def _get_additional_data_for_user_initiated_event(
    event: DbUserEvent, users_by_id: Dict[str, User]
) -> Iterator[Tuple[str, Any]]:
    initiator_id = event.data.get('initiator_id')
    if initiator_id is not None:
        yield 'initiator', users_by_id[initiator_id]
