"""
testfixtures.verification_token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.verification_token.models import Purpose, Token


def create_verification_token(user_id, purpose, *, created_at=None):
    token = Token(user_id, purpose)

    if created_at is not None:
        token.created_at = created_at

    return token


def create_verification_token_for_email_address_confirmation(user_id):
    purpose = Purpose.email_address_confirmation
    return create_verification_token(user_id, purpose)
