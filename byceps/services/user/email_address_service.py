"""
byceps.services.user.email_address_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from flask_babel import gettext

from ...database import db
from ...events.user import (
    UserEmailAddressChanged,
    UserEmailAddressConfirmed,
    UserEmailAddressInvalidated,
)
from ...typing import UserID
from ...util.l10n import force_user_locale

from ..email import (
    config_service as email_config_service,
    service as email_service,
)
from ..email.transfer.models import NameAndAddress
from ..site import service as site_service
from ..site.transfer.models import SiteID
from ..user import (
    command_service as user_command_service,
    service as user_service,
)
from ..verification_token import service as verification_token_service
from ..verification_token.transfer.models import Token

from . import log_service as user_log_service
from .transfer.models import User


def send_email_address_confirmation_email_for_site(
    user: User,
    email_address: str,
    site_id: SiteID,
) -> None:
    site = site_service.get_site(site_id)

    email_config = email_config_service.get_config(site.brand_id)
    sender = email_config.sender

    send_email_address_confirmation_email(
        user, email_address, site.server_name, sender
    )


def send_email_address_confirmation_email(
    user: User,
    email_address: str,
    server_name: str,
    sender: NameAndAddress,
) -> None:
    recipients = [email_address]

    verification_token = (
        verification_token_service.create_for_email_address_confirmation(
            user.id, email_address
        )
    )
    confirmation_url = (
        f'https://{server_name}/users/email_address/'
        f'confirmation/{verification_token.token}'
    )

    with force_user_locale(user):
        recipient_screen_name = _get_user_screen_name_or_fallback(user)
        subject = gettext(
            '%(screen_name)s, please verify your email address',
            screen_name=recipient_screen_name,
        )
        body = (
            gettext('Hello %(screen_name)s,', screen_name=recipient_screen_name)
            + '\n\n'
            + gettext(
                'please verify your email address by accessing this URL: %(url)s',
                url=confirmation_url,
            )
        )

    email_service.enqueue_email(sender, recipients, subject, body)


class EmailAddressConfirmationFailed(Exception):
    pass


def confirm_email_address_via_verification_token(
    verification_token: Token,
) -> UserEmailAddressConfirmed:
    """Confirm the email address of the user account assigned with that
    verification token.
    """
    user_id = verification_token.user_id

    token_email_address = verification_token.data.get('email_address')
    if not token_email_address:
        raise EmailAddressConfirmationFailed('Token contains no email address.')

    event = confirm_email_address(user_id, token_email_address)

    verification_token_service.delete_token(verification_token.token)

    return event


def confirm_email_address(
    user_id: UserID, email_address_to_confirm: str
) -> UserEmailAddressConfirmed:
    """Confirm the email address of the user account."""
    user = user_service.get_db_user(user_id)

    if user.email_address is None:
        raise EmailAddressConfirmationFailed(
            'Account has no email address assigned.'
        )

    if user.email_address != email_address_to_confirm:
        raise EmailAddressConfirmationFailed('Email addresses do not match.')

    user.email_address_verified = True

    log_entry_data = {'email_address': user.email_address}
    log_entry = user_log_service.build_entry(
        'user-email-address-confirmed', user.id, log_entry_data
    )
    db.session.add(log_entry)

    db.session.commit()

    return UserEmailAddressConfirmed(
        occurred_at=log_entry.occurred_at,
        initiator_id=user.id,
        initiator_screen_name=user.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


def invalidate_email_address(
    user_id: UserID, reason: str, *, initiator_id: Optional[UserID] = None
) -> UserEmailAddressInvalidated:
    """Invalidate the user's email address by marking it as unverified.

    This might be appropriate if an email to the user's address bounced
    because of a permanent issue (unknown mailbox, unknown domain, etc.)
    but not a temporary one (for example: mailbox full).
    """
    user = user_service.get_db_user(user_id)

    initiator: Optional[User]
    if initiator_id is not None:
        initiator = user_service.get_user(initiator_id)
    else:
        initiator = None

    user.email_address_verified = False

    log_entry_data = {
        'email_address': user.email_address,
        'reason': reason,
    }
    if initiator:
        log_entry_data['initiator_id'] = str(initiator.id)
    log_entry = user_log_service.build_entry(
        'user-email-address-invalidated', user.id, log_entry_data
    )
    db.session.add(log_entry)

    db.session.commit()

    return UserEmailAddressInvalidated(
        occurred_at=log_entry.occurred_at,
        initiator_id=initiator.id if initiator else None,
        initiator_screen_name=initiator.screen_name if initiator else None,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


def send_email_address_change_email_for_site(
    user: User,
    new_email_address: str,
    site_id: SiteID,
) -> None:
    site = site_service.get_site(site_id)

    email_config = email_config_service.get_config(site.brand_id)
    sender = email_config.sender

    send_email_address_change_email(
        user, new_email_address, site.server_name, sender
    )


def send_email_address_change_email(
    user: User,
    new_email_address: str,
    server_name: str,
    sender: NameAndAddress,
) -> None:
    recipients = [new_email_address]

    verification_token = (
        verification_token_service.create_for_email_address_change(
            user.id, new_email_address
        )
    )
    confirmation_url = (
        f'https://{server_name}/users/email_address/'
        f'change/{verification_token.token}'
    )

    with force_user_locale(user):
        recipient_screen_name = _get_user_screen_name_or_fallback(user)
        subject = gettext(
            '%(screen_name)s, please verify your email address',
            screen_name=recipient_screen_name,
        )
        body = (
            gettext('Hello %(screen_name)s,', screen_name=recipient_screen_name)
            + '\n\n'
            + gettext(
                'please verify your email address by accessing this URL: %(url)s',
                url=confirmation_url,
            )
        )

    email_service.enqueue_email(sender, recipients, subject, body)


class EmailAddressChangeFailed(Exception):
    pass


def change_email_address(verification_token: Token) -> UserEmailAddressChanged:
    """Change the email address of the user account assigned with that
    verification token.
    """
    new_email_address = verification_token.data.get('new_email_address')
    if not new_email_address:
        raise EmailAddressChangeFailed('Token contains no email address.')

    user = user_service.get_db_user(verification_token.user_id)
    verified = True
    initiator = user

    event = user_command_service.change_email_address(
        user.id, new_email_address, verified, initiator.id
    )

    verification_token_service.delete_token(verification_token.token)

    return event


def _get_user_screen_name_or_fallback(user: User) -> str:
    return user.screen_name or f'user-{user.id}'
