"""
byceps.services.verification_token.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from ...database import db
from ...typing import UserID

from .dbmodels import Token as DbToken
from .transfer.models import Purpose


def create_for_email_address_confirmation(user_id: UserID) -> DbToken:
    return _create_token(user_id, Purpose.email_address_confirmation)


def create_for_password_reset(user_id: UserID) -> DbToken:
    return _create_token(user_id, Purpose.password_reset)


def create_for_terms_consent(user_id: UserID) -> DbToken:
    return _create_token(user_id, Purpose.terms_consent)


def _create_token(user_id: UserID, purpose: Purpose) -> DbToken:
    token = DbToken(user_id, purpose)

    db.session.add(token)
    db.session.commit()

    return token


def delete_token(token: str) -> None:
    """Delete the token."""
    db.session.query(DbToken) \
        .filter_by(token=token) \
        .delete()

    db.session.commit()


def find_for_email_address_confirmation_by_token(
    token_value: str,
) -> Optional[DbToken]:
    purpose = Purpose.email_address_confirmation
    return _find_for_purpose_by_token(token_value, purpose)


def find_for_password_reset_by_token(token_value: str) -> Optional[DbToken]:
    purpose = Purpose.password_reset
    return _find_for_purpose_by_token(token_value, purpose)


def find_for_terms_consent_by_token(token_value: str) -> Optional[DbToken]:
    purpose = Purpose.terms_consent
    return _find_for_purpose_by_token(token_value, purpose)


def _find_for_purpose_by_token(
    token_value: str, purpose: Purpose
) -> Optional[DbToken]:
    return DbToken.query \
        .filter_by(token=token_value) \
        .for_purpose(purpose) \
        .first()


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
