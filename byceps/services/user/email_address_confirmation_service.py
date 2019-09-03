"""
byceps.services.user.email_address_confirmation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..email import service as email_service
from ..site import service as site_service
from ..site.transfer.models import SiteID
from ..verification_token.models import Token
from ..verification_token import service as verification_token_service


def send_email_address_confirmation_email(recipient_email_address: str,
                                          recipient_screen_name: str,
                                          verification_token: Token,
                                          email_config_id: str, site_id: SiteID
                                         ) -> None:
    email_config = email_service.get_config(email_config_id)
    sender = email_config.sender

    site = site_service.get_site(site_id)

    confirmation_url = 'https://{}/users/email_address/confirmation/{}' \
        .format(site.server_name, verification_token.token)

    subject = '{}, bitte bestätige deine E-Mail-Adresse' \
        .format(recipient_screen_name)
    body = (
        'Hallo {0},\n\n'
        'bitte bestätige deine E-Mail-Adresse, indem du diese URL abrufst: {1}'
    ).format(recipient_screen_name, confirmation_url)
    recipients = [recipient_email_address]

    email_service.enqueue_email(sender, recipients, subject, body)


def confirm_email_address(verification_token: Token) -> None:
    """Confirm the email address of the user assigned with that
    verification token.
    """
    user = verification_token.user

    user.email_address_verified = True
    user.enabled = True
    db.session.commit()

    verification_token_service.delete_token(verification_token)
