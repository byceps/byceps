"""
byceps.services.authentication.password.authn_password_reset_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from ....util.l10n import force_user_locale

from ...email import service as email_service
from ...email.transfer.models import NameAndAddress
from ...user import user_service
from ...user.transfer.models import User
from ...verification_token import service as verification_token_service
from ...verification_token.transfer.models import VerificationToken

from . import authn_password_service


def prepare_password_reset(
    user: User,
    email_address: str,
    url_root: str,
    sender: NameAndAddress,
) -> None:
    """Create a verification token for password reset and email it to
    the user's address.
    """
    recipients = [email_address]

    verification_token = verification_token_service.create_for_password_reset(
        user.id
    )
    confirmation_url = f'{url_root}authentication/password/reset/token/{verification_token.token}'

    screen_name = user.screen_name or f'user-{user.id}'

    with force_user_locale(user):
        subject = gettext(
            '%(screen_name)s, this is how you can set a new password',
            screen_name=screen_name,
        )
        body = (
            gettext('Hello %(screen_name)s,', screen_name=screen_name)
            + '\n\n'
            + gettext(
                'you can set a new password here: %(url)s', url=confirmation_url
            )
        )

    email_service.enqueue_email(sender, recipients, subject, body)


def reset_password(
    verification_token: VerificationToken, password: str
) -> None:
    """Reset the user's password."""
    user = user_service.get_db_user(verification_token.user_id)

    verification_token_service.delete_token(verification_token.token)

    authn_password_service.update_password_hash(user.id, password, user.id)
