"""
byceps.services.user.email_address_confirmation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import url_for


from ...blueprints.user.email_address import views  # Make `url_for` work.

from ...database import db
from ...typing import BrandID

from ..email import service as email_service
from ..verification_token.models import Token
from ..verification_token import service as verification_token_service


def send_email_address_confirmation_email(recipient_email_address: str,
                                          recipient_screen_name: str,
                                          verification_token: Token,
                                          brand_id: BrandID) -> None:
    sender_address = email_service.get_sender_address_for_brand(brand_id)

    confirmation_url = url_for('user_email_address.confirm',
                               token=verification_token.token,
                               _external=True)

    subject = '{}, bitte bestätige deine E-Mail-Adresse' \
        .format(recipient_screen_name)
    body = (
        'Hallo {0},\n\n'
        'bitte bestätige deine E-Mail-Adresse, indem du diese URL abrufst: {1}'
    ).format(recipient_screen_name, confirmation_url)
    recipients = [recipient_email_address]

    email_service.enqueue_email(sender_address, recipients, subject, body)


def confirm_email_address(verification_token: Token) -> None:
    """Confirm the email address of the user assigned with that
    verification token.
    """
    user = verification_token.user

    user.email_address_verified = True
    user.enabled = True
    db.session.commit()

    verification_token_service.delete_token(verification_token)
