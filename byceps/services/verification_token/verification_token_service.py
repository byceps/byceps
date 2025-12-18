"""
byceps.services.verification_token.verification_token_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime, timedelta
import secrets

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.user import user_service
from byceps.services.user.models.user import User, UserID

from .dbmodels import DbVerificationToken
from .models import (
    ConsentToken,
    EmailAddressChangeToken,
    EmailAddressConfirmationToken,
    PasswordResetToken,
    Purpose,
    VerificationToken,
)


def create_for_consent(user: User) -> ConsentToken:
    vt = _create_token(user, Purpose.consent)
    return _to_consent_token(vt)


def create_for_email_address_change(
    user: User, new_email_address: str
) -> EmailAddressChangeToken:
    data = {'new_email_address': new_email_address}
    vt = _create_token(user, Purpose.email_address_change, data=data)
    return _to_email_address_change_token(vt)


def create_for_email_address_confirmation(
    user: User, email_address: str
) -> EmailAddressConfirmationToken:
    data = {'email_address': email_address}
    vt = _create_token(user, Purpose.email_address_confirmation, data=data)
    return _to_email_address_confirmation_token(vt)


def create_for_password_reset(user: User) -> PasswordResetToken:
    vt = _create_token(user, Purpose.password_reset)
    return _to_password_reset_token(vt)


def _create_token(
    user: User, purpose: Purpose, *, data: dict[str, str] | None = None
) -> VerificationToken:
    token_value = _generate_token_value()
    created_at = datetime.utcnow()

    db_token = DbVerificationToken(
        token_value, created_at, user.id, purpose, data=data
    )

    db.session.add(db_token)
    db.session.commit()

    return _db_entity_to_token(db_token, user)


def _generate_token_value() -> str:
    """Return a cryptographic, URL-safe token."""
    return secrets.token_urlsafe()


def delete_token(token: str) -> None:
    """Delete the token."""
    db.session.execute(
        delete(DbVerificationToken).where(DbVerificationToken.token == token)
    )
    db.session.commit()


def delete_tokens_for_user(user_id: UserID) -> None:
    """Delete all session tokens that belong to the user."""
    db.session.execute(
        delete(DbVerificationToken).where(
            DbVerificationToken.user_id == user_id
        )
    )
    db.session.commit()


def delete_old_tokens(created_before: datetime) -> int:
    """Delete tokens which were created before the given date.

    Return the number of deleted tokens.
    """
    result = db.session.execute(
        delete(DbVerificationToken).where(
            DbVerificationToken.created_at < created_before
        )
    )
    db.session.commit()

    num_deleted = result.rowcount
    return num_deleted


def find_for_consent_by_token(token_value: str) -> ConsentToken | None:
    vt = _find_for_purpose_by_token(token_value, Purpose.consent)
    if vt is None:
        return None

    return _to_consent_token(vt)


def find_for_email_address_change_by_token(
    token_value: str,
) -> EmailAddressChangeToken | None:
    vt = _find_for_purpose_by_token(token_value, Purpose.email_address_change)
    if vt is None:
        return None

    return _to_email_address_change_token(vt)


def find_for_email_address_confirmation_by_token(
    token_value: str,
) -> EmailAddressConfirmationToken | None:
    vt = _find_for_purpose_by_token(
        token_value, Purpose.email_address_confirmation
    )
    if vt is None:
        return None

    return _to_email_address_confirmation_token(vt)


def find_for_password_reset_by_token(
    token_value: str,
) -> PasswordResetToken | None:
    vt = _find_for_purpose_by_token(token_value, Purpose.password_reset)
    if vt is None:
        return None

    return _to_password_reset_token(vt)


def _find_for_purpose_by_token(
    token_value: str, purpose: Purpose
) -> VerificationToken | None:
    db_token = db.session.scalars(
        select(DbVerificationToken)
        .filter_by(token=token_value)
        .filter_by(_purpose=purpose.name)
    ).first()

    if db_token is None:
        return None

    user = user_service.get_user(db_token.user_id)

    return _db_entity_to_token(db_token, user)


def _db_entity_to_token(
    db_token: DbVerificationToken, user: User
) -> VerificationToken:
    return VerificationToken(
        token=db_token.token,
        created_at=db_token.created_at,
        user=user,
        purpose=db_token.purpose,
        data=db_token.data if db_token.data is not None else {},
    )


def _to_consent_token(vt: VerificationToken) -> ConsentToken:
    return ConsentToken(
        token=vt.token,
        created_at=vt.created_at,
        user=vt.user,
    )


def _to_email_address_change_token(
    vt: VerificationToken,
) -> EmailAddressChangeToken:
    return EmailAddressChangeToken(
        token=vt.token,
        created_at=vt.created_at,
        user=vt.user,
        new_email_address=vt.data['new_email_address'],
    )


def _to_email_address_confirmation_token(
    vt: VerificationToken,
) -> EmailAddressConfirmationToken:
    return EmailAddressConfirmationToken(
        token=vt.token,
        created_at=vt.created_at,
        user=vt.user,
        email_address=vt.data['email_address'],
    )


def _to_password_reset_token(vt: VerificationToken) -> PasswordResetToken:
    return PasswordResetToken(
        token=vt.token,
        created_at=vt.created_at,
        user=vt.user,
    )


def count_tokens_by_purpose() -> dict[Purpose, int]:
    """Count verification tokens, grouped by purpose."""
    rows = (
        db.session.execute(
            select(
                DbVerificationToken._purpose,
                db.func.count(DbVerificationToken.token),
            ).group_by(DbVerificationToken._purpose)
        )
        .tuples()
        .all()
    )

    counts_by_name = dict(rows)

    return {purpose: counts_by_name.get(purpose.name, 0) for purpose in Purpose}


def is_expired(token: PasswordResetToken) -> bool:
    """Return `True` if the token has expired, i.e. it is no longer valid."""
    now = datetime.utcnow()
    expires_after = timedelta(hours=24)
    return now >= (token.created_at + expires_after)
