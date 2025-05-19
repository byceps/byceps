"""
byceps.services.user.user_deletion_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

User account anonymization and removal

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.database import db
from byceps.services.authn.password import authn_password_service
from byceps.services.authn.session import authn_session_service
from byceps.services.authz import authz_service
from byceps.services.newsletter import newsletter_command_service
from byceps.services.user import (
    user_domain_service,
    user_log_service,
    user_service,
)
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.log import UserLogEntry
from byceps.services.user.models.user import User
from byceps.services.verification_token import verification_token_service

from .events import UserAccountDeletedEvent


def delete_account(
    user: User, initiator: User, reason: str
) -> UserAccountDeletedEvent:
    """Delete the user account."""
    event, log_entry = user_domain_service.delete_account(
        user, initiator, reason
    )

    _persist_account_deletion(user, initiator, log_entry)

    authn_session_service.delete_session_tokens_for_user(user.id)
    authn_password_service.delete_password_hash(user.id)
    verification_token_service.delete_tokens_for_user(user.id)
    newsletter_command_service.unsubscribe_user_from_lists(
        user, log_entry.occurred_at, initiator
    )

    return event


def _persist_account_deletion(
    user: User, initiator: User, log_entry: UserLogEntry
) -> None:
    db_user = user_service.get_db_user(user.id)

    db_user.deleted = True

    _anonymize_account(db_user)

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    authz_service.deassign_all_roles_from_user(
        user, initiator=initiator, commit=False
    )

    db.session.commit()


def _anonymize_account(db_user: DbUser) -> None:
    """Remove user details from the account."""
    db_user.screen_name = None
    db_user.email_address = None
    db_user.avatar_id = None
    db_user.legacy_id = None

    # Remove details.
    db_user.detail.first_name = None
    db_user.detail.last_name = None
    db_user.detail.date_of_birth = None
    db_user.detail.country = None
    db_user.detail.postal_code = None
    db_user.detail.city = None
    db_user.detail.street = None
    db_user.detail.phone_number = None
    db_user.detail.internal_comment = None
    db_user.detail.extras = None
