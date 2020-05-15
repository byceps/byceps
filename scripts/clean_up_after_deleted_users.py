#!/usr/bin/env python

"""Remove data for user accounts that have been marked as deleted.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Callable, Set

import click

from byceps.database import db
from byceps.services.authentication.password.models import Credential
from byceps.services.authentication.session.models.session_token import (
    RecentLogin,
    SessionToken,
)
from byceps.services.authorization.models import UserRole
from byceps.services.board.models.last_category_view import (
    LastCategoryView as BoardLastCategoryView,
)
from byceps.services.board.models.last_topic_view import (
    LastTopicView as BoardLastTopicView,
)
from byceps.services.consent.models.consent import Consent
from byceps.services.newsletter.models import (
    SubscriptionUpdate as NewsletterSubscriptionUpdate,
)
from byceps.services.user.models.event import UserEvent
from byceps.services.user import service as user_service
from byceps.services.user_avatar.models import (
    AvatarSelection as UserAvatarSelection,
)
from byceps.services.verification_token.models import Token as VerificationToken
from byceps.typing import UserID
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context


@click.command()
@click.option(
    '--dry-run',
    is_flag=True,
    help='determine but do not delete affected records',
)
@click.argument('user_ids', nargs=-1, required=True)
def execute(dry_run, user_ids):
    user_ids = set(user_ids)

    check_for_undeleted_accounts(user_ids)

    def delete(label: str, delete_func: Callable) -> None:
        delete_records(label, delete_func, user_ids)

    delete('authentication credentials', delete_authn_credentials)
    delete('recent logins', delete_authn_recent_logins)
    delete('session tokens', delete_authn_session_tokens)
    delete('authorization role assignments', delete_authz_user_roles)
    delete('board category view marks', delete_board_category_lastviews)
    delete('board topic view marks', delete_board_topic_lastviews)
    delete('consents', delete_consents)
    delete(
        'newsletter subscription updates',
        delete_newsletter_subscription_updates,
    )
    delete('user avatar selections', delete_user_avatar_selections)
    delete('user events', delete_user_events)
    delete('verification tokens', delete_verification_tokens)

    if not dry_run:
        db.session.commit()


def check_for_undeleted_accounts(user_ids: Set[UserID]) -> None:
    users = user_service.find_users(user_ids)

    non_deleted_users = [u for u in users if not u.deleted]
    if non_deleted_users:
        user_ids_string = ', '.join(str(u.id) for u in non_deleted_users)
        raise click.BadParameter(
            f'These user accounts are not marked as deleted: {user_ids_string}'
        )


def delete_records(
    label: str, delete_func: Callable, user_ids: Set[UserID]
) -> None:
    click.secho(f'Deleting {label} ... ', nl=False)
    affected = delete_func(user_ids)
    click.secho(str(affected), fg='yellow')


def delete_authn_credentials(user_ids: Set[UserID]) -> int:
    """Delete authentication credentials for the given users."""
    return _execute_delete_for_users_query(Credential, user_ids)


def delete_authn_recent_logins(user_ids: Set[UserID]) -> int:
    """Delete recent logins for the given users."""
    return _execute_delete_for_users_query(RecentLogin, user_ids)


def delete_authn_session_tokens(user_ids: Set[UserID]) -> int:
    """Delete session tokens for the given users."""
    return _execute_delete_for_users_query(SessionToken, user_ids)


def delete_authz_user_roles(user_ids: Set[UserID]) -> int:
    """Delete authorization role assignments from the given users."""
    return _execute_delete_for_users_query(UserRole, user_ids)


def delete_board_category_lastviews(user_ids: Set[UserID]) -> int:
    """Delete last board category view marks for the given users."""
    return _execute_delete_for_users_query(BoardLastCategoryView, user_ids)


def delete_board_topic_lastviews(user_ids: Set[UserID]) -> int:
    """Delete last board topic view marks for the given users."""
    return _execute_delete_for_users_query(BoardLastTopicView, user_ids)


def delete_consents(user_ids: Set[UserID]) -> int:
    """Delete consents from the given users."""
    return _execute_delete_for_users_query(Consent, user_ids)


def delete_newsletter_subscription_updates(user_ids: Set[UserID]) -> int:
    """Delete newsletter subscription updates for the given users."""
    return _execute_delete_for_users_query(
        NewsletterSubscriptionUpdate, user_ids
    )


def delete_user_avatar_selections(user_ids: Set[UserID]) -> int:
    """Delete user avatar selections (but not user avatar records and
    image files at this point) for the given users.
    """
    return _execute_delete_for_users_query(UserAvatarSelection, user_ids)


def delete_user_events(user_ids: Set[UserID]) -> int:
    """Delete user events (execpt for those that justify the deletion)
    for the given users.
    """
    return (
        db.session.query(UserEvent)
        .filter(UserEvent.user_id.in_(user_ids))
        .filter(UserEvent.event_type != 'user-deleted')
        .delete(synchronize_session=False)
    )


def delete_verification_tokens(user_ids: Set[UserID]) -> int:
    """Delete verification tokens for the given users."""
    return _execute_delete_for_users_query(VerificationToken, user_ids)


def _execute_delete_for_users_query(model, user_ids: Set[UserID]) -> int:
    """Execute (but not commit) deletions, return number of affected rows."""
    return (
        db.session.query(model)
        .filter(model.user_id.in_(user_ids))
        .delete(synchronize_session=False)
    )


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
