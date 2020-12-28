"""
byceps.announce.irc.user
~~~~~~~~~~~~~~~~~~~~~~~~

Announce user events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.user import (
    _UserEvent,
    UserAccountCreated,
    UserAccountDeleted,
    UserAccountSuspended,
    UserAccountUnsuspended,
    UserDetailsUpdated,
    UserEmailAddressInvalidated,
    UserScreenNameChanged,
)
from ...services.webhooks.transfer.models import OutgoingWebhook

from ..common import user
from ..helpers import call_webhook


def announce_user_account_created(
    event: UserAccountCreated, webhook: OutgoingWebhook
) -> None:
    """Announce that a user account has been created."""
    text = user.assemble_text_for_user_account_created(event)

    send_user_message(event, webhook, text)


def announce_user_screen_name_changed(
    event: UserScreenNameChanged, webhook: OutgoingWebhook
) -> None:
    """Announce that a user's screen name has been changed."""
    text = user.assemble_text_for_user_screen_name_changed(event)

    send_user_message(event, webhook, text)


def announce_user_email_address_invalidated(
    event: UserEmailAddressInvalidated, webhook: OutgoingWebhook
) -> None:
    """Announce that a user's email address has been invalidated."""
    text = user.assemble_text_for_user_email_address_invalidated(event)

    send_user_message(event, webhook, text)


def announce_user_details_updated_changed(
    event: UserDetailsUpdated, webhook: OutgoingWebhook
) -> None:
    """Announce that a user's details have been changed."""
    text = user.assemble_text_for_user_details_updated_changed(event)

    send_user_message(event, webhook, text)


def announce_user_account_suspended(
    event: UserAccountSuspended, webhook: OutgoingWebhook
) -> None:
    """Announce that a user account has been suspended."""
    text = user.assemble_text_for_user_account_suspended(event)

    send_user_message(event, webhook, text)


def announce_user_account_unsuspended(
    event: UserAccountUnsuspended, webhook: OutgoingWebhook
) -> None:
    """Announce that a user account has been unsuspended."""
    text = user.assemble_text_for_user_account_unsuspended(event)

    send_user_message(event, webhook, text)


def announce_user_account_deleted(
    event: UserAccountDeleted, webhook: OutgoingWebhook
) -> None:
    """Announce that a user account has been deleted."""
    text = user.assemble_text_for_user_account_deleted(event)

    send_user_message(event, webhook, text)


# helpers


def send_user_message(
    event: _UserEvent, webhook: OutgoingWebhook, text: str
) -> None:
    scope = 'user'
    scope_id = None

    call_webhook(webhook, text)
