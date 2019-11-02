"""
byceps.services.user.email_address_confirmation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db
from ...events.user import UserEmailAddressConfirmed
from ...typing import UserID

from ..email import service as email_service
from ..site import service as site_service
from ..site.transfer.models import SiteID
from ..verification_token.models import Token
from ..verification_token import service as verification_token_service

from . import command_service, event_service as user_event_service


def send_email_address_confirmation_email(
    recipient_email_address: str,
    recipient_screen_name: str,
    user_id: UserID,
    site_id: SiteID,
) -> None:
    site = site_service.get_site(site_id)

    email_config = email_service.get_config(site.email_config_id)
    sender = email_config.sender

    verification_token = verification_token_service.create_for_email_address_confirmation(
        user_id
    )
    confirmation_url = (
        f'https://{site.server_name}/users/email_address/'
        f'confirmation/{verification_token.token}'
    )

    subject = f'{recipient_screen_name}, bitte bestätige deine E-Mail-Adresse'
    body = (
        f'Hallo {recipient_screen_name},\n\n'
        f'bitte bestätige deine E-Mail-Adresse, indem du diese URL abrufst: {confirmation_url}'
    )
    recipients = [recipient_email_address]

    email_service.enqueue_email(sender, recipients, subject, body)


def confirm_email_address(
    verification_token: Token
) -> UserEmailAddressConfirmed:
    """Confirm the email address of the user assigned with that
    verification token.
    """
    user = verification_token.user

    user.email_address_verified = True
    db.session.commit()

    # Currently, the user's e-mail address cannot be changed, but that
    # might be allowed in the future. At that point, the verification
    # token should be extended to include the e-mail address it refers
    # to, and that value should be persisted with user event instead.
    data = {'email_address': user.email_address}
    event = user_event_service.create_event('email-address-confirmed', user.id, data)

    if not user.initialized:
        command_service.initialize_account(user.id)

    verification_token_service.delete_token(verification_token)

    return UserEmailAddressConfirmed(
        occurred_at=event.occurred_at, user_id=user.id, initiator_id=user.id
    )
