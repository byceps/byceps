#!/usr/bin/env python

"""Remove data for user accounts that have been marked as deleted.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Callable

import click
from sqlalchemy import delete

from byceps.database import db
from byceps.services.authentication.password.dbmodels import DbCredential
from byceps.services.authentication.session.dbmodels.recent_login import (
    DbRecentLogin,
)
from byceps.services.authentication.session.dbmodels.session_token import (
    DbSessionToken,
)
from byceps.services.authorization.dbmodels import DbUserRole
from byceps.services.board.dbmodels.last_category_view import (
    DbLastCategoryView as DbBoardLastCategoryView,
)
from byceps.services.board.dbmodels.last_topic_view import (
    DbLastTopicView as DbBoardLastTopicView,
)
from byceps.services.consent.dbmodels import DbConsent
from byceps.services.newsletter.dbmodels import (
    DbSubscription as DbNewsletterSubscription,
    DbSubscriptionUpdate as DbNewsletterSubscriptionUpdate,
)
from byceps.services.user.dbmodels.log import DbUserLogEntry
from byceps.services.user import user_service
from byceps.services.verification_token.dbmodels import DbVerificationToken
from byceps.typing import UserID

from _util import call_with_app_context


@click.command()
@click.option(
    '--dry-run',
    is_flag=True,
    help='determine but do not delete affected records',
)
@click.argument('user_ids', nargs=-1, required=True)
def execute(dry_run, user_ids) -> None:
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
    delete('newsletter subscriptions', delete_newsletter_subscriptions)
    delete(
        'newsletter subscription updates',
        delete_newsletter_subscription_updates,
    )
    delete('user log entries', delete_user_log_entries)
    delete('verification tokens', delete_verification_tokens)

    if not dry_run:
        db.session.commit()


def check_for_undeleted_accounts(user_ids: set[UserID]) -> None:
    users = user_service.get_users(user_ids)

    non_deleted_users = [u for u in users if not u.deleted]
    if non_deleted_users:
        user_ids_string = ', '.join(str(u.id) for u in non_deleted_users)
        raise click.BadParameter(
            f'These user accounts are not marked as deleted: {user_ids_string}'
        )


def delete_records(
    label: str, delete_func: Callable, user_ids: set[UserID]
) -> None:
    click.secho(f'Deleting {label} ... ', nl=False)
    affected = delete_func(user_ids)
    click.secho(str(affected), fg='yellow')


def delete_authn_credentials(user_ids: set[UserID]) -> int:
    """Delete authentication credentials for the given users."""
    return _execute_delete_for_users_query(DbCredential, user_ids)


def delete_authn_recent_logins(user_ids: set[UserID]) -> int:
    """Delete recent logins for the given users."""
    return _execute_delete_for_users_query(DbRecentLogin, user_ids)


def delete_authn_session_tokens(user_ids: set[UserID]) -> int:
    """Delete session tokens for the given users."""
    return _execute_delete_for_users_query(DbSessionToken, user_ids)


def delete_authz_user_roles(user_ids: set[UserID]) -> int:
    """Delete authorization role assignments from the given users."""
    return _execute_delete_for_users_query(DbUserRole, user_ids)


def delete_board_category_lastviews(user_ids: set[UserID]) -> int:
    """Delete last board category view marks for the given users."""
    return _execute_delete_for_users_query(DbBoardLastCategoryView, user_ids)


def delete_board_topic_lastviews(user_ids: set[UserID]) -> int:
    """Delete last board topic view marks for the given users."""
    return _execute_delete_for_users_query(DbBoardLastTopicView, user_ids)


def delete_consents(user_ids: set[UserID]) -> int:
    """Delete consents from the given users."""
    return _execute_delete_for_users_query(DbConsent, user_ids)


def delete_newsletter_subscriptions(user_ids: set[UserID]) -> int:
    """Delete newsletter subscriptions for the given users."""
    return _execute_delete_for_users_query(DbNewsletterSubscription, user_ids)


def delete_newsletter_subscription_updates(user_ids: set[UserID]) -> int:
    """Delete newsletter subscription updates for the given users."""
    return _execute_delete_for_users_query(
        DbNewsletterSubscriptionUpdate, user_ids
    )


def delete_user_log_entries(user_ids: set[UserID]) -> int:
    """Delete user log entries (except for those that justify the
    deletion) for the given users.
    """
    return db.session.execute(
        delete(DbUserLogEntry)
        .filter(DbUserLogEntry.user_id.in_(user_ids))
        .filter(DbUserLogEntry.event_type != 'user-deleted')
    )


def delete_verification_tokens(user_ids: set[UserID]) -> int:
    """Delete verification tokens for the given users."""
    return _execute_delete_for_users_query(DbVerificationToken, user_ids)


def _execute_delete_for_users_query(model, user_ids: set[UserID]) -> int:
    """Execute (but not commit) deletions, return number of affected rows."""
    return db.session.execute(delete(model).filter(model.user_id.in_(user_ids)))


if __name__ == '__main__':
    call_with_app_context(execute)
