# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.verification_token_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from .verification_token_models import Purpose, Token


def build_for_email_address_confirmation(user):
    return Token(user, Purpose.email_address_confirmation)


def build_for_password_reset(user):
    return Token(user, Purpose.password_reset)


def find_for_email_address_confirmation_by_user(user):
    return Token.query \
        .filter_by(user=user) \
        .for_purpose(Purpose.email_address_confirmation) \
        .first()


def find_for_email_address_confirmation_by_token(token):
    purpose = Purpose.email_address_confirmation
    return find_for_purpose_by_token(token, purpose)


def find_for_password_reset_by_token(token):
    purpose = Purpose.password_reset
    return find_for_purpose_by_token(token, purpose )


def find_for_purpose_by_token(token, purpose):
    return Token.query \
        .filter_by(token=token) \
        .for_purpose(purpose) \
        .first()
