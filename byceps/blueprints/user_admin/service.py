"""
byceps.blueprints.user_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Any, Dict, Iterator, Tuple

from ...database import db
from ...services.newsletter import service as newsletter_service
from ...services.shop.order import service as order_service
from ...services.terms import service as terms_service
from ...services.user import event_service
from ...services.user.models.detail import UserDetail
from ...services.user.models.event import UserEvent, UserEventData
from ...services.user.models.user import User, UserTuple
from ...services.user import service as user_service
from ...services.user_avatar import service as avatar_service
from ...typing import UserID

from .models import UserStateFilter


def get_users_paginated(page, per_page, *, search_term=None, state_filter=None):
    """Return the users to show on the specified page, optionally
    filtered by search term or 'enabled' flag.
    """
    query = User.query \
        .options(db.joinedload('detail')) \
        .order_by(User.created_at.desc())

    query = _filter_by_state(query, state_filter)

    if search_term:
        query = _filter_by_search_term(query, search_term)

    return query.paginate(page, per_page)


def _filter_by_search_term(query, search_term):
    ilike_pattern = '%{}%'.format(search_term)

    return query \
        .join(UserDetail) \
        .filter(
            db.or_(
                User.email_address.ilike(ilike_pattern),
                User.screen_name.ilike(ilike_pattern),
                UserDetail.first_names.ilike(ilike_pattern),
                UserDetail.last_name.ilike(ilike_pattern)
            )
        )


def _filter_by_state(query, state_filter):
    if state_filter == UserStateFilter.enabled:
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


def get_events(user_id: UserID) -> Iterator[UserEventData]:
    events = event_service.get_events_for_user(user_id)
    events.insert(0, _fake_user_creation_event(user_id))
    events.extend(_fake_avatar_update_events(user_id))
    events.extend(_fake_newsletter_subscription_update_events(user_id))
    events.extend(_fake_order_events(user_id))
    events.extend(_fake_terms_consent_events(user_id))

    user_ids = {event.data['initiator_id']
                for event in events
                if 'initiator_id' in event.data}
    users = user_service.find_users(user_ids)
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


def _fake_user_creation_event(user_id: UserID) -> UserEvent:
    user = user_service.find_user(user_id)
    if user is None:
        raise ValueError('Unknown user ID')

    data = {
        # This must be adjusted as soon as existing users (admins) are
        # allowed to create users.
        #'initiator_id': str(initiator.id),
    }

    return UserEvent(user.created_at, 'user-created', user.id, data)


def _fake_avatar_update_events(user_id: UserID) -> Iterator[UserEvent]:
    """Yield the user's avatar updates as volatile events."""
    avatars = avatar_service.get_avatars_uploaded_by_user(user_id)

    for avatar in avatars:
        data = {
            'initiator_id': str(user_id),
            'url': avatar.url,
        }

        yield UserEvent(avatar.created_at, 'avatar-updated', user_id, data)


def _fake_newsletter_subscription_update_events(user_id: UserID) \
        -> Iterator[UserEvent]:
    """Yield the user's newsletter subscription updates as volatile events."""
    updates = newsletter_service.get_subscription_updates_for_user(user_id)

    for update in updates:
        event_type = 'newsletter-{}'.format(update.state.name)

        data = {
            'brand_id': update.brand_id,
            'initiator_id': str(user_id),
        }

        yield UserEvent(update.expressed_at, event_type, user_id, data)


def _fake_order_events(user_id: UserID) -> Iterator[UserEvent]:
    """Yield the orders placed by the user as volatile events."""
    orders = order_service.get_orders_placed_by_user(user_id)

    for order in orders:
        data = {
            'initiator_id': str(user_id),
            'order': order.to_tuple(),
        }

        yield UserEvent(order.created_at, 'order-placed', user_id, data)


def _fake_terms_consent_events(user_id: UserID) -> Iterator[UserEvent]:
    """Yield the user's consents to terms as volatile events."""
    consents = terms_service.get_consents_by_user(user_id)

    for consent in consents:
        data = {
            'initiator_id': str(user_id),
            'version_title': consent.version.title,
        }

        yield UserEvent(consent.expressed_at, 'terms-consent-expressed',
                        user_id, data)


def _get_additional_data(event: UserEvent, users_by_id: Dict[UserID, UserTuple]
                        ) -> Iterator[Tuple[str, Any]]:
    if event.event_type in {
            'user-created',
            'user-deleted',
            'user-disabled',
            'user-enabled',
            'user-suspended',
            'user-unsuspended',
            'password-updated',
            'avatar-updated',
            'newsletter-requested',
            'newsletter-declined',
            'order-placed',
            'terms-consent-expressed',
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
        users_by_id: Dict[UserID, UserTuple]) -> Iterator[Tuple[str, Any]]:
    initiator_id = event.data.get('initiator_id')
    if initiator_id is not None:
        yield 'initiator', users_by_id[initiator_id]
