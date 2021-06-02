"""
byceps.services.verification_token.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional

from ...database import db
from ...typing import UserID

from .dbmodels import Token as DbToken
from .transfer.models import Purpose, Token


def create_for_email_address_change(
    user_id: UserID, new_email_address: str
) -> Token:
    data = {'new_email_address': new_email_address}
    return _create_token(user_id, Purpose.email_address_change, data=data)


def create_for_email_address_confirmation(
    user_id: UserID, email_address: str
) -> Token:
    data = {'email_address': email_address}
    return _create_token(user_id, Purpose.email_address_confirmation, data=data)


def create_for_password_reset(user_id: UserID) -> Token:
    return _create_token(user_id, Purpose.password_reset)


def create_for_terms_consent(user_id: UserID) -> Token:
    return _create_token(user_id, Purpose.terms_consent)


def _create_token(
    user_id: UserID, purpose: Purpose, *, data: Optional[dict[str, str]] = None
) -> Token:
    token = DbToken(user_id, purpose, data=data)

    db.session.add(token)
    db.session.commit()

    return _db_entity_to_token(token)


def delete_token(token: str) -> None:
    """Delete the token."""
    db.session.query(DbToken) \
        .filter_by(token=token) \
        .delete()

    db.session.commit()


def find_for_email_address_change_by_token(token_value: str) -> Optional[Token]:
    purpose = Purpose.email_address_change
    return _find_for_purpose_by_token(token_value, purpose)


def find_for_email_address_confirmation_by_token(
    token_value: str,
) -> Optional[Token]:
    purpose = Purpose.email_address_confirmation
    return _find_for_purpose_by_token(token_value, purpose)


def find_for_password_reset_by_token(token_value: str) -> Optional[Token]:
    purpose = Purpose.password_reset
    return _find_for_purpose_by_token(token_value, purpose)


def find_for_terms_consent_by_token(token_value: str) -> Optional[Token]:
    purpose = Purpose.terms_consent
    return _find_for_purpose_by_token(token_value, purpose)


def _find_for_purpose_by_token(
    token_value: str, purpose: Purpose
) -> Optional[Token]:
    token = DbToken.query \
        .filter_by(token=token_value) \
        .for_purpose(purpose) \
        .first()

    if token is None:
        return None

    return _db_entity_to_token(token)


def _db_entity_to_token(token: DbToken) -> Token:
    return Token(
        token=token.token,
        created_at=token.created_at,
        user_id=token.user_id,
        purpose=token.purpose,
        data=token.data if token.data is not None else {},
    )


def count_tokens_by_purpose() -> dict[Purpose, int]:
    """Count verification tokens, grouped by purpose."""
    rows = db.session \
        .query(
            DbToken._purpose,
            db.func.count(DbToken.token)
        ) \
        .group_by(DbToken._purpose) \
        .all()

    counts_by_name = dict(rows)

    return {purpose: counts_by_name[purpose.name] for purpose in Purpose}


def is_expired(token: Token) -> bool:
    """Return `True` if the token has expired, i.e. it is no longer valid."""
    if token.purpose != Purpose.password_reset:
        return False

    now = datetime.utcnow()
    expires_after = timedelta(hours=24)
    return now >= (token.created_at + expires_after)
