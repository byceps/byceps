"""
byceps.services.user.email_address_verification_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...database import db
from ...events.user import (
    UserEmailAddressConfirmed,
    UserEmailAddressInvalidated,
)
from ...typing import UserID

from ..email import service as email_service
from ..site import service as site_service
from ..site.transfer.models import SiteID
from ..user import service as user_service
from ..verification_token.models import Token
from ..verification_token import service as verification_token_service

from . import event_service as user_event_service


def send_email_address_confirmation_email(
    recipient_email_address: str,
    recipient_screen_name: str,
    user_id: UserID,
    site_id: SiteID,
) -> None:
    site = site_service.get_site(site_id)

    email_config = email_service.get_config(site.brand_id)
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
    verification_token: Token,
) -> UserEmailAddressConfirmed:
    """Confirm the email address of the user assigned with that
    verification token.
    """
    user = user_service.get_db_user(verification_token.user_id)

    user.email_address_verified = True
    db.session.commit()

    # Currently, the user's e-mail address cannot be changed, but that
    # might be allowed in the future. At that point, the verification
    # token should be extended to include the e-mail address it refers
    # to, and that value should be persisted with user event instead.
    event_data = {'email_address': user.email_address}
    event = user_event_service.create_event(
        'user-email-address-confirmed', user.id, event_data
    )

    verification_token_service.delete_token(verification_token)

    return UserEmailAddressConfirmed(
        occurred_at=event.occurred_at,
        initiator_id=user.id,
        initiator_screen_name=user.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


def invalidate_email_address(
    user_id: UserID, reason: str, *, initiator_id: Optional[UserID] = None,
) -> UserEmailAddressInvalidated:
    """Invalidate the user's email address by marking it as unverified.

    This might be appropriate if an email to the user's address bounced
    because of a permanent issue (unknown mailbox, unknown domain, etc.)
    but not a temporary one (for example: mailbox full).
    """
    user = user_service.get_db_user(user_id)

    if initiator_id is not None:
        initiator = user_service.get_user(initiator_id)
    else:
        initiator = None

    user.email_address_verified = False
    db.session.commit()

    event_data = {
        'email_address': user.email_address,
        'reason': reason,
    }
    if initiator:
        event_data['initiator_id'] = str(initiator.id)
    event = user_event_service.create_event(
        'user-email-address-invalidated', user.id, event_data
    )

    return UserEmailAddressInvalidated(
        occurred_at=event.occurred_at,
        initiator_id=initiator.id if initiator else None,
        initiator_screen_name=initiator.screen_name if initiator else None,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )
