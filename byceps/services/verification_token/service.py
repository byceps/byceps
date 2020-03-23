"""
byceps.services.verification_token.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...database import db
from ...typing import UserID

from .models import Purpose, Token as DbToken


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


def delete_token(token: DbToken) -> None:
    db.session.delete(token)
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
