"""
byceps.services.authentication.password.reset_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...email import service as email_service
from ...email.transfer.models import Sender
from ...user.models.user import User
from ...verification_token.models import Token
from ...verification_token import service as verification_token_service

from . import service as password_service


def prepare_password_reset(
    user: User, url_root: str, *, sender: Optional[Sender] = None
) -> None:
    """Create a verification token for password reset and email it to
    the user's address.
    """
    verification_token = verification_token_service.create_for_password_reset(
        user.id
    )

    confirmation_url = f'{url_root}authentication/password/reset/token/{verification_token.token}'

    recipients = [user.email_address]
    subject = f'{user.screen_name}, so kannst du ein neues Passwort festlegen'
    body = (
        f'Hallo {user.screen_name},\n\n'
        f'dort kannst du ein neues Passwort festlegen:\n{confirmation_url}'
    )

    email_service.enqueue_email(sender, recipients, subject, body)


def reset_password(verification_token: Token, password: str) -> None:
    """Reset the user's password."""
    user = verification_token.user

    verification_token_service.delete_token(verification_token)

    password_service.update_password_hash(user.id, password, user.id)
