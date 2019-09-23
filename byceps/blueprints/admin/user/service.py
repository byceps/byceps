"""
byceps.blueprints.admin.user.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import defaultdict
from operator import attrgetter
from typing import Any, Dict, Iterator, List, Sequence, Set, Tuple

from ....database import db
from ....services.consent import consent_service
from ....services.newsletter import service as newsletter_service
from ....services.newsletter.transfer.models import List as NewsletterList
from ....services.party import service as party_service
from ....services.party.transfer.models import Party
from ....services.shop.order import service as order_service
from ....services.ticketing.models.ticket import Ticket as DbTicket
from ....services.ticketing import attendance_service, ticket_service
from ....services.user import event_service
from ....services.user.models.detail import UserDetail
from ....services.user.models.event import UserEvent, UserEventData
from ....services.user.models.user import User as DbUser
from ....services.user import service as user_service
from ....services.user.transfer.models import User
from ....services.user_avatar import service as avatar_service
from ....typing import PartyID, UserID

from .models import UserStateFilter


def get_users_paginated(page, per_page, *, search_term=None, state_filter=None):
    """Return the users to show on the specified page, optionally
    filtered by search term or 'enabled' flag.
    """
    query = DbUser.query \
        .options(db.joinedload('detail')) \
        .order_by(DbUser.created_at.desc())

    query = _filter_by_state(query, state_filter)

    if search_term:
        query = _filter_by_search_term(query, search_term)

    return query.paginate(page, per_page)


def _filter_by_state(query, state_filter):
    if state_filter == UserStateFilter.uninitialized:
        return query \
            .filter_by(initialized=False) \
            .filter_by(suspended=False) \
            .filter_by(deleted=False)
    elif state_filter == UserStateFilter.enabled:
        return query \
            .filter_by(enabled=True) \
            .filter_by(suspended=False) \
            .filter_by(deleted=False)
    elif state_filter == UserStateFilter.disabled:
        return query \
            .filter_by(enabled=False) \
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
    ilike_pattern = '%{}%'.format(search_term)

    return query \
        .join(UserDetail) \
        .filter(
            db.or_(
                DbUser.email_address.ilike(ilike_pattern),
                DbUser.screen_name.ilike(ilike_pattern),
                UserDetail.first_names.ilike(ilike_pattern),
                UserDetail.last_name.ilike(ilike_pattern)
            )
        )


def get_parties_and_tickets(user_id: UserID
                           ) -> List[Tuple[Party, List[DbTicket]]]:
    """Return tickets the user uses or manages, and the related parties."""
    tickets = ticket_service.find_tickets_related_to_user(user_id)

    tickets_by_party_id = _group_tickets_by_party_id(tickets)

    party_ids = set(tickets_by_party_id.keys())
    parties_by_id = _get_parties_by_id(party_ids)

    parties_and_tickets = [
        (parties_by_id[party_id], tickets)
        for party_id, tickets in tickets_by_party_id.items()]

    parties_and_tickets.sort(key=lambda x: x[0].starts_at, reverse=True)

    return parties_and_tickets


def _group_tickets_by_party_id(tickets: Sequence[DbTicket]
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


def get_newsletter_subscriptions(user_id: UserID
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

    user_ids = {event.data['initiator_id']
                for event in events
                if 'initiator_id' in event.data}
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


def _fake_avatar_update_events(user_id: UserID) -> Iterator[UserEvent]:
    """Yield the user's avatar updates as volatile events."""
    avatars = avatar_service.get_avatars_uploaded_by_user(user_id)

    for avatar in avatars:
        data = {
            'initiator_id': str(user_id),
            'url': avatar.url,
        }

        yield UserEvent(avatar.created_at, 'avatar-updated', user_id, data)


def _fake_consent_events(user_id: UserID) -> Iterator[UserEvent]:
    """Yield the user's consents as volatile events."""
    consents = consent_service.get_consents_by_user(user_id)

    for consent in consents:
        data = {
            'initiator_id': str(user_id),
            'subject_title': consent.subject.title,
        }

        yield UserEvent(consent.expressed_at, 'consent-expressed', user_id,
                        data)


def _fake_newsletter_subscription_update_events(user_id: UserID) \
        -> Iterator[UserEvent]:
    """Yield the user's newsletter subscription updates as volatile events."""
    lists = newsletter_service.get_all_lists()
    lists_by_id = {list_.id: list_ for list_ in lists}

    updates = newsletter_service.get_subscription_updates_for_user(user_id)

    for update in updates:
        event_type = 'newsletter-{}'.format(update.state.name)

        list_ = lists_by_id[update.list_id]

        data = {
            'list_': list_,
            'initiator_id': str(user_id),
        }

        yield UserEvent(update.expressed_at, event_type, user_id, data)


def _fake_order_events(user_id: UserID) -> Iterator[UserEvent]:
    """Yield the orders placed by the user as volatile events."""
    orders = order_service.get_orders_placed_by_user(user_id)

    for order in orders:
        data = {
            'initiator_id': str(user_id),
            'order': order.to_transfer_object(),
        }

        yield UserEvent(order.created_at, 'order-placed', user_id, data)


def _get_additional_data(event: UserEvent, users_by_id: Dict[str, User]
                        ) -> Iterator[Tuple[str, Any]]:
    if event.event_type in {
            'user-created',
            'user-deleted',
            'user-disabled',
            'user-email-address-changed',
            'user-enabled',
            'user-initialized',
            'user-screen-name-changed',
            'user-suspended',
            'user-unsuspended',
            'password-updated',
            'avatar-updated',
            'consent-expressed',
            'newsletter-requested',
            'newsletter-declined',
            'order-placed',
            'orgaflag-added',
            'orgaflag-removed',
            'privacy-policy-accepted',
            'role-assigned',
            'role-deassigned',
    }:
        yield from _get_additional_data_for_user_initiated_event(
            event, users_by_id)

    if event.event_type in {
            'user-deleted',
            'user-suspended',
            'user-unsuspended',
    }:
        yield 'reason', event.data['reason']


def _get_additional_data_for_user_initiated_event(event: UserEvent,
        users_by_id: Dict[str, User]) -> Iterator[Tuple[str, Any]]:
    initiator_id = event.data.get('initiator_id')
    if initiator_id is not None:
        yield 'initiator', users_by_id[initiator_id]
