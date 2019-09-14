"""
byceps.services.authentication.password.reset_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from flask import url_for

from ....database import db

from ...email import service as email_service
from ...email.transfer.models import Sender
from ...user.models.user import User
from ...verification_token.models import Token
from ...verification_token import service as verification_token_service

from . import service as password_service


def prepare_password_reset(user: User, *, sender: Optional[Sender]=None
                          ) -> None:
    """Create a verification token for password reset and email it to
    the user's address.
    """
    verification_token = verification_token_service \
        .create_for_password_reset(user.id)

    confirmation_url = url_for('authentication.password_reset_form',
                               token=verification_token.token,
                               _external=True)

    recipients = [user.email_address]
    subject = '{0.screen_name}, so kannst du ein neues Passwort festlegen' \
        .format(user)
    body = (
        'Hallo {0.screen_name},\n\n'
        'du kannst ein neues Passwort festlegen, indem du diese URL abrufst: {1}'
    ).format(user, confirmation_url)

    email_service.enqueue_email(sender, recipients, subject, body)


def reset_password(verification_token: Token, password: str) -> None:
    """Reset the user's password."""
    user = verification_token.user

    verification_token_service.delete_token(verification_token)

    password_service.update_password_hash(user.id, password, user.id)
