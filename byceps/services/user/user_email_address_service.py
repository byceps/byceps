"""
byceps.services.user.user_email_address_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from flask_babel import gettext

from byceps.database import db
from byceps.events.user import (
    UserEmailAddressChangedEvent,
    UserEmailAddressConfirmedEvent,
    UserEmailAddressInvalidatedEvent,
)
from byceps.services.email import email_config_service, email_service
from byceps.services.email.models import NameAndAddress
from byceps.services.site import site_service
from byceps.services.site.models import SiteID
from byceps.services.user import user_command_service, user_service
from byceps.services.verification_token import verification_token_service
from byceps.services.verification_token.models import VerificationToken
from byceps.typing import UserID
from byceps.util.l10n import force_user_locale
from byceps.util.result import Err, Ok, Result

from . import user_log_service
from .models.user import User


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


def confirm_email_address_via_verification_token(
    verification_token: VerificationToken,
) -> Result[UserEmailAddressConfirmedEvent, str]:
    """Confirm the email address of the user account assigned with that
    verification token.
    """
    user_id = verification_token.user_id

    token_email_address = verification_token.data.get('email_address')
    if not token_email_address:
        return Err('Token contains no email address.')

    confirmation_result = confirm_email_address(user_id, token_email_address)
    if confirmation_result.is_err():
        return Err(confirmation_result.unwrap_err())

    event = confirmation_result.unwrap()

    verification_token_service.delete_token(verification_token.token)

    return Ok(event)


def confirm_email_address(
    user_id: UserID, email_address_to_confirm: str
) -> Result[UserEmailAddressConfirmedEvent, str]:
    """Confirm the email address of the user account."""
    user = user_service.get_db_user(user_id)

    if user.email_address is None:
        return Err('Account has no email address assigned.')

    if user.email_address != email_address_to_confirm:
        return Err('Email addresses do not match.')

    occurred_at = datetime.utcnow()

    user.email_address_verified = True

    log_entry_data = {'email_address': user.email_address}
    log_entry = user_log_service.build_entry(
        'user-email-address-confirmed',
        user.id,
        log_entry_data,
        occurred_at=occurred_at,
    )
    db.session.add(log_entry)

    db.session.commit()

    event = UserEmailAddressConfirmedEvent(
        occurred_at=occurred_at,
        initiator_id=user.id,
        initiator_screen_name=user.screen_name,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    return Ok(event)


def invalidate_email_address(
    user_id: UserID, reason: str, *, initiator_id: UserID | None = None
) -> UserEmailAddressInvalidatedEvent:
    """Invalidate the user's email address by marking it as unverified.

    This might be appropriate if an email to the user's address bounced
    because of a permanent issue (unknown mailbox, unknown domain, etc.)
    but not a temporary one (for example: mailbox full).
    """
    user = user_service.get_db_user(user_id)

    occurred_at = datetime.utcnow()

    initiator: User | None
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
        'user-email-address-invalidated',
        user.id,
        log_entry_data,
        occurred_at=occurred_at,
    )
    db.session.add(log_entry)

    db.session.commit()

    return UserEmailAddressInvalidatedEvent(
        occurred_at=occurred_at,
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


def change_email_address(
    verification_token: VerificationToken,
) -> Result[UserEmailAddressChangedEvent, str]:
    """Change the email address of the user account assigned with that
    verification token.
    """
    new_email_address = verification_token.data.get('new_email_address')
    if not new_email_address:
        return Err('Token contains no email address.')

    user = user_service.get_db_user(verification_token.user_id)
    verified = True
    initiator = user

    event = user_command_service.change_email_address(
        user.id, new_email_address, verified, initiator.id
    )

    verification_token_service.delete_token(verification_token.token)

    return Ok(event)


def _get_user_screen_name_or_fallback(user: User) -> str:
    return user.screen_name or f'user-{user.id}'
