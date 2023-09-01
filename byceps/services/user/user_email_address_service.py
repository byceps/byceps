"""
byceps.services.user.user_email_address_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

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
from byceps.services.user import (
    user_command_service,
    user_domain_service,
    user_log_service,
    user_service,
)
from byceps.services.user.models.log import UserLogEntry
from byceps.services.user.models.user import User
from byceps.services.verification_token import verification_token_service
from byceps.services.verification_token.models import VerificationToken
from byceps.typing import UserID
from byceps.util.l10n import force_user_locale
from byceps.util.result import Err, Ok, Result


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
            user, email_address
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
    user = verification_token.user

    token_email_address = verification_token.data.get('email_address')
    if not token_email_address:
        return Err('Verification token contains no email address.')

    confirmation_result = confirm_email_address(user, token_email_address)
    if confirmation_result.is_err():
        return Err(confirmation_result.unwrap_err())

    event = confirmation_result.unwrap()

    verification_token_service.delete_token(verification_token.token)

    return Ok(event)


def confirm_email_address(
    user: User, email_address_to_confirm: str
) -> Result[UserEmailAddressConfirmedEvent, str]:
    """Confirm the email address of the user account."""
    current_email_address = user_service.get_email_address_data(user.id)

    result = user_domain_service.confirm_email_address(
        user, current_email_address, email_address_to_confirm
    )

    if result.is_err():
        return Err(result.unwrap_err())

    event, log_entry = result.unwrap()

    _persist_email_address_confirmation(user.id, log_entry)

    return Ok(event)


def _persist_email_address_confirmation(
    user_id: UserID, log_entry: UserLogEntry
) -> None:
    db_user = user_service.get_db_user(user_id)

    db_user.email_address_verified = True

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()


def invalidate_email_address(
    user: User, reason: str, *, initiator: User | None = None
) -> UserEmailAddressInvalidatedEvent:
    """Invalidate the user's email address by marking it as unverified.

    This might be appropriate if an email to the user's address bounced
    because of a permanent issue (unknown mailbox, unknown domain, etc.)
    but not a temporary one (for example: mailbox full).
    """
    email_address = user_service.get_email_address_data(user.id)

    event, log_entry = user_domain_service.invalidate_email_address(
        user, email_address, reason, initiator=initiator
    )

    _persist_email_address_invalidation(user.id, log_entry)

    return event


def _persist_email_address_invalidation(
    user_id: UserID, log_entry: UserLogEntry
) -> None:
    db_user = user_service.get_db_user(user_id)

    db_user.email_address_verified = False

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()


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
            user, new_email_address
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

    user = verification_token.user
    verified = True
    initiator = user

    event = user_command_service.change_email_address(
        user, new_email_address, verified, initiator
    )

    verification_token_service.delete_token(verification_token.token)

    return Ok(event)


def _get_user_screen_name_or_fallback(user: User) -> str:
    return user.screen_name or f'user-{user.id}'
