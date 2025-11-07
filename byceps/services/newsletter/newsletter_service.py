"""
byceps.services.newsletter.newsletter_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator

from byceps.services.user.models.user import UserID

from . import newsletter_repository
from .dbmodels import DbList, DbSubscriptionUpdate
from .models import List, ListID, Subscriber, SubscriptionUpdate


def find_list(list_id: ListID) -> List | None:
    """Return the list with that ID, or `None` if not found."""
    db_list = newsletter_repository.find_list(list_id)

    if db_list is None:
        return None

    return _db_entity_to_list(db_list)


def get_all_lists() -> list[List]:
    """Return all lists."""
    db_lists = newsletter_repository.get_all_lists()

    return [_db_entity_to_list(db_list) for db_list in db_lists]


def count_subscribers_to_list(list_id: ListID) -> int:
    """Return the number of users that are currently subscribed to that list."""
    return newsletter_repository.count_subscribers_to_list(list_id)


def get_subscribers_to_list(list_id: ListID) -> Iterator[Subscriber]:
    """Yield screen name and email address of the users that are
    currently subscribed to the list.

    This excludes user accounts that are
    - not initialized,
    - have no or an unverified email address,
    - are suspended, or
    - have been deleted.
    """
    screen_names_and_email_addresses = (
        newsletter_repository.get_subscribers_to_list(list_id)
    )

    for screen_name, email_address in screen_names_and_email_addresses:
        yield Subscriber(
            screen_name=screen_name or 'unnamed',
            email_address=email_address,
        )


def get_subscription_updates_for_user(
    user_id: UserID,
) -> list[SubscriptionUpdate]:
    """Return subscription updates made by the user, for any list."""
    db_subscription_updates = (
        newsletter_repository.get_subscription_updates_for_user(user_id)
    )

    return [
        _db_entity_to_subscription_update(db_subscription_update)
        for db_subscription_update in db_subscription_updates
    ]


def get_lists_user_is_subscribed_to(user_id: UserID) -> set[List]:
    """Return the lists the user is subscribed to."""
    return {
        list_
        for list_ in get_all_lists()
        if is_user_subscribed_to_list(user_id, list_.id)
    }


def is_user_subscribed_to_list(user_id: UserID, list_id: ListID) -> bool:
    """Return if the user is subscribed to the list or not."""
    return newsletter_repository.is_user_subscribed_to_list(user_id, list_id)


def _db_entity_to_list(db_list: DbList) -> List:
    return List(
        id=db_list.id,
        title=db_list.title,
    )


def _db_entity_to_subscription_update(
    db_subscription_update: DbSubscriptionUpdate,
) -> SubscriptionUpdate:
    return SubscriptionUpdate(
        user_id=db_subscription_update.user_id,
        list_id=db_subscription_update.list_id,
        expressed_at=db_subscription_update.expressed_at,
        state=db_subscription_update.state,
    )
