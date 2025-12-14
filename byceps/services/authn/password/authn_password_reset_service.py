"""
byceps.services.authn.password.authn_password_reset_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import force_locale, gettext

from byceps.services.authn.events import PasswordUpdatedEvent
from byceps.services.email import email_service
from byceps.services.email.models import NameAndAddress
from byceps.services.user import user_service
from byceps.services.user.models.user import Password, User
from byceps.services.verification_token import verification_token_service
from byceps.services.verification_token.models import PasswordResetToken
from byceps.util.l10n import get_default_locale

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

    reset_token = verification_token_service.create_for_password_reset(user)
    confirmation_url = (
        f'{url_root}authentication/password/reset/token/{reset_token.token}'
    )

    screen_name = user.screen_name or f'user-{user.id}'

    locale = user_service.find_locale(user.id) or get_default_locale()

    with force_locale(locale):
        subject = gettext(
            '%(screen_name)s, this is how you can set a new password',
            screen_name=screen_name,
        )
        body = (
            gettext('Hello %(screen_name)s,', screen_name=screen_name)
            + '\n\n'
            + gettext('you can set a new password here:')
            + '\n'
            + confirmation_url
        )

    email_service.enqueue_email(sender, recipients, subject, body)


def reset_password(
    reset_token: PasswordResetToken, password: Password
) -> PasswordUpdatedEvent:
    """Reset the user's password."""
    user = reset_token.user

    verification_token_service.delete_token(reset_token.token)

    return authn_password_service.update_password_hash(user, password, user)
