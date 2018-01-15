"""
byceps.services.authentication.password.reset_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import url_for

from ....database import db
from ....typing import BrandID

from ...email import service as email_service
from ...user.models.user import User
from ...verification_token.models import Token
from ...verification_token import service as verification_token_service

from . import service as password_service


def prepare_password_reset(user: User, brand_id: BrandID) -> None:
    """Create a verification token for password reset and email it to
    the user's address.
    """
    verification_token = verification_token_service \
        .build_for_password_reset(user.id)

    db.session.add(verification_token)
    db.session.commit()

    _send_password_reset_email(user, verification_token, brand_id)


def _send_password_reset_email(user: User, verification_token: Token,
                               brand_id: BrandID) -> None:
    sender_address = email_service.get_sender_address_for_brand(brand_id)

    confirmation_url = url_for('authentication.password_reset_form',
                               token=verification_token.token,
                               _external=True)

    subject = '{0.screen_name}, so kannst du ein neues Passwort festlegen' \
        .format(user)
    body = (
        'Hallo {0.screen_name},\n\n'
        'du kannst ein neues Passwort festlegen indem du diese URL abrufst: {1}'
    ).format(user, confirmation_url)
    recipients = [user.email_address]

    email_service.enqueue_email(sender_address, recipients, subject, body)


def reset_password(verification_token: Token, password: str) -> None:
    """Reset the user's password."""
    user = verification_token.user

    db.session.delete(verification_token)
    db.session.commit()

    password_service.update_password_hash(user.id, password, user.id)
