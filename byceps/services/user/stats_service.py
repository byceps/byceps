"""
byceps.services.user.stats_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime, timedelta

from .models.user import User as DbUser


def count_users() -> int:
    """Return the number of users."""
    return DbUser.query \
        .count()


def count_users_created_since(delta: timedelta) -> int:
    """Return the number of user accounts created since `delta` ago."""
    filter_starts_at = datetime.utcnow() - delta

    return DbUser.query \
        .filter(DbUser.created_at >= filter_starts_at) \
        .count()


def count_active_users() -> int:
    """Return the number of active user accounts.

    Uninitialized, suspended or deleted accounts are excluded.
    """
    return DbUser.query \
        .filter_by(initialized=True) \
        .filter_by(suspended=False) \
        .filter_by(deleted=False) \
        .count()


def count_uninitialized_users() -> int:
    """Return the number of uninitialized user accounts.

    Suspended or deleted accounts are excluded.
    """
    return DbUser.query \
        .filter_by(initialized=False) \
        .filter_by(suspended=False) \
        .filter_by(deleted=False) \
        .count()


def count_suspended_users() -> int:
    """Return the number of suspended user accounts."""
    return DbUser.query \
        .filter_by(suspended=True) \
        .filter_by(deleted=False) \
        .count()


def count_deleted_users() -> int:
    """Return the number of deleted user accounts."""
    return DbUser.query \
        .filter_by(deleted=True) \
        .count()
