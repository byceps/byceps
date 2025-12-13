"""
byceps.services.user.user_deletion_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

User account anonymization and removal

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.authn.password import authn_password_service
from byceps.services.authn.session import authn_session_service
from byceps.services.authz import authz_service
from byceps.services.newsletter import newsletter_command_service
from byceps.services.user import user_domain_service
from byceps.services.user.log import user_log_service
from byceps.services.user.models.user import User
from byceps.services.verification_token import verification_token_service

from . import user_repository
from .events import UserAccountDeletedEvent


def delete_account(
    user: User, initiator: User, reason: str
) -> UserAccountDeletedEvent:
    """Delete the user account."""
    event, log_entry = user_domain_service.delete_account(
        user, initiator, reason
    )

    authz_service.deassign_all_roles_from_user(
        user, initiator=initiator, commit=False
    )

    db_log_entry = user_log_service.to_db_entry(log_entry)

    user_repository.delete_user(user, initiator, db_log_entry)

    authn_session_service.delete_session_tokens_for_user(user.id)
    authn_password_service.delete_password_hash(user.id)
    verification_token_service.delete_tokens_for_user(user.id)
    newsletter_command_service.unsubscribe_user_from_lists(
        user, log_entry.occurred_at, initiator
    )

    return event
