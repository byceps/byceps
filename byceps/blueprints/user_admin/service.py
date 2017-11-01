"""
byceps.blueprints.user_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Iterator

from ...database import db
from ...services.user import event_service
from ...services.user.models.detail import UserDetail
from ...services.user.models.event import UserEvent, UserEventData
from ...services.user.models.user import User
from ...services.user import service as user_service
from ...typing import UserID

from .models import UserEnabledFilter


def get_users_paginated(page, per_page, *, search_term=None,
                        enabled_filter=None):
    """Return the users to show on the specified page, optionally
    filtered by search term or 'enabled' flag.
    """
    query = User.query \
        .options(db.joinedload('detail')) \
        .order_by(User.created_at.desc())

    query = _filter_by_enabled_flag(query, enabled_filter)

    if search_term:
        query = _filter_by_search_term(query, search_term)

    return query.paginate(page, per_page)


def _filter_by_search_term(query, search_term):
    ilike_pattern = '%{}%'.format(search_term)

    return query \
        .join(UserDetail) \
        .filter(
            db.or_(
                User.screen_name.ilike(ilike_pattern),
                UserDetail.first_names.ilike(ilike_pattern),
                UserDetail.last_name.ilike(ilike_pattern)
            )
        )


def _filter_by_enabled_flag(query, enabled_filter):
    if enabled_filter == UserEnabledFilter.enabled:
        return query.filter_by(enabled=True)
    elif enabled_filter == UserEnabledFilter.disabled:
        return query.filter_by(enabled=False)
    else:
        return query


def get_events(user_id: UserID) -> Iterator[UserEventData]:
    events = event_service.get_events_for_user(user_id)
    events.insert(0, _fake_user_creation_event(user_id))

    for event in events:
        yield {
            'event': event.event_type,
            'occurred_at': event.occurred_at,
            'data': event.data,
        }


def _fake_user_creation_event(user_id: UserID) -> UserEvent:
    user = user_service.find_user(user_id)
    if user is None:
        raise ValueError('Unknown user ID')

    data = {
        # This must be adjusted as soon as existing users (admins) are
        # allowed to create users.
        'initiator_id': str(user.id),
    }

    return UserEvent(user.created_at, 'user-created', user.id, data)
