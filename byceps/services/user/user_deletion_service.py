"""
byceps.services.user.user_deletion_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

User account anonymization and removal

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...database import db
from ...events.user import UserAccountDeleted
from ...typing import UserID

from ..authentication.password import authn_password_service
from ..authentication.session import authn_session_service
from ..authorization import authz_service
from ..verification_token import verification_token_service

from .dbmodels.user import DbUser
from . import user_log_service, user_service


def delete_account(
    user_id: UserID, initiator_id: UserID, reason: str
) -> UserAccountDeleted:
    """Delete the user account."""
    user = user_service.get_db_user(user_id)
    initiator = user_service.get_user(initiator_id)

    user_screen_name_before_anonymization = user.screen_name

    user.deleted = True
    _anonymize_account(user)

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
        user.id, initiator.id, commit=False
    )

    db.session.commit()

    authn_session_service.delete_session_tokens_for_user(user.id)
    authn_password_service.delete_password_hash(user.id)
    verification_token_service.delete_tokens_for_user(user.id)

    return UserAccountDeleted(
        occurred_at=log_entry.occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        user_id=user.id,
        user_screen_name=user_screen_name_before_anonymization,
    )


def _anonymize_account(user: DbUser) -> None:
    """Remove user details from the account."""
    user.screen_name = None
    user.email_address = None
    user.avatar_id = None
    user.legacy_id = None

    # Remove details.
    user.detail.first_name = None
    user.detail.last_name = None
    user.detail.date_of_birth = None
    user.detail.country = None
    user.detail.zip_code = None
    user.detail.city = None
    user.detail.street = None
    user.detail.phone_number = None
    user.detail.internal_comment = None
    user.detail.extras = None
