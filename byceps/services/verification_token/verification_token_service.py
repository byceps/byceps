"""
byceps.services.verification_token.verification_token_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import delete, select

from byceps.database import db
from byceps.typing import UserID

from .dbmodels import DbVerificationToken
from .models import Purpose, VerificationToken


def create_for_email_address_change(
    user_id: UserID, new_email_address: str
) -> VerificationToken:
    data = {'new_email_address': new_email_address}
    return _create_token(user_id, Purpose.email_address_change, data=data)


def create_for_email_address_confirmation(
    user_id: UserID, email_address: str
) -> VerificationToken:
    data = {'email_address': email_address}
    return _create_token(user_id, Purpose.email_address_confirmation, data=data)


def create_for_password_reset(user_id: UserID) -> VerificationToken:
    return _create_token(user_id, Purpose.password_reset)


def create_for_consent(user_id: UserID) -> VerificationToken:
    return _create_token(user_id, Purpose.consent)


def _create_token(
    user_id: UserID, purpose: Purpose, *, data: dict[str, str] | None = None
) -> VerificationToken:
    token = DbVerificationToken(user_id, purpose, data=data)

    db.session.add(token)
    db.session.commit()

    return _db_entity_to_token(token)


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


def find_for_email_address_change_by_token(
    token_value: str,
) -> VerificationToken | None:
    purpose = Purpose.email_address_change
    return _find_for_purpose_by_token(token_value, purpose)


def find_for_email_address_confirmation_by_token(
    token_value: str,
) -> VerificationToken | None:
    purpose = Purpose.email_address_confirmation
    return _find_for_purpose_by_token(token_value, purpose)


def find_for_password_reset_by_token(
    token_value: str,
) -> VerificationToken | None:
    purpose = Purpose.password_reset
    return _find_for_purpose_by_token(token_value, purpose)


def find_for_consent_by_token(token_value: str) -> VerificationToken | None:
    purpose = Purpose.consent
    return _find_for_purpose_by_token(token_value, purpose)


def _find_for_purpose_by_token(
    token_value: str, purpose: Purpose
) -> VerificationToken | None:
    token = db.session.scalars(
        select(DbVerificationToken)
        .filter_by(token=token_value)
        .filter_by(_purpose=purpose.name)
    ).first()

    if token is None:
        return None

    return _db_entity_to_token(token)


def _db_entity_to_token(token: DbVerificationToken) -> VerificationToken:
    return VerificationToken(
        token=token.token,
        created_at=token.created_at,
        user_id=token.user_id,
        purpose=token.purpose,
        data=token.data if token.data is not None else {},
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


def is_expired(token: VerificationToken) -> bool:
    """Return `True` if the token has expired, i.e. it is no longer valid."""
    if token.purpose != Purpose.password_reset:
        return False

    now = datetime.utcnow()
    expires_after = timedelta(hours=24)
    return now >= (token.created_at + expires_after)
