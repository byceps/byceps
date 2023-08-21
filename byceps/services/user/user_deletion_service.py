"""
byceps.services.user.user_deletion_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

User account anonymization and removal

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.database import db
from byceps.events.user import UserAccountDeletedEvent
from byceps.services.authentication.password import authn_password_service
from byceps.services.authentication.session import authn_session_service
from byceps.services.authorization import authz_service
from byceps.services.user.models.user import User
from byceps.services.verification_token import verification_token_service

from . import user_log_service, user_service
from .dbmodels.user import DbUser


def delete_account(
    user: User, initiator: User, reason: str
) -> UserAccountDeletedEvent:
    """Delete the user account."""
    db_user = user_service.get_db_user(user.id)

    user_screen_name_before_anonymization = db_user.screen_name

    db_user.deleted = True
    _anonymize_account(db_user)

    log_entry = user_log_service.build_entry(
        'user-deleted',
        user.id,
        {
            'initiator_id': str(initiator.id),
            'reason': reason,
        },
    )
    db.session.add(log_entry)

    # Deassign authorization roles.
    authz_service.deassign_all_roles_from_user(
        user.id, initiator=initiator, commit=False
    )

    db.session.commit()

    authn_session_service.delete_session_tokens_for_user(user.id)
    authn_password_service.delete_password_hash(user.id)
    verification_token_service.delete_tokens_for_user(user.id)

    return UserAccountDeletedEvent(
        occurred_at=log_entry.occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=user.id,
        user_screen_name=user_screen_name_before_anonymization,
    )


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
    db_user.detail.zip_code = None
    db_user.detail.city = None
    db_user.detail.street = None
    db_user.detail.phone_number = None
    db_user.detail.internal_comment = None
    db_user.detail.extras = None
