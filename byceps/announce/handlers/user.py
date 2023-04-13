"""
byceps.announce.handlers.user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce user events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...events.user import (
    UserAccountCreated,
    UserAccountDeleted,
    UserAccountSuspended,
    UserAccountUnsuspended,
    UserDetailsUpdated,
    UserEmailAddressChanged,
    UserEmailAddressInvalidated,
    UserScreenNameChanged,
)
from ...services.webhooks.models import OutgoingWebhook

from ..helpers import Announcement
from ..text_assembly import user


def announce_user_account_created(
    event: UserAccountCreated, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a user account has been created."""
    text = user.assemble_text_for_user_account_created(event)
    return Announcement(text)


def announce_user_screen_name_changed(
    event: UserScreenNameChanged, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a user's screen name has been changed."""
    text = user.assemble_text_for_user_screen_name_changed(event)
    return Announcement(text)


def announce_user_email_address_changed(
    event: UserEmailAddressChanged, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a user's email address has been changed."""
    text = user.assemble_text_for_user_email_address_changed(event)
    return Announcement(text)


def announce_user_email_address_invalidated(
    event: UserEmailAddressInvalidated, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a user's email address has been invalidated."""
    text = user.assemble_text_for_user_email_address_invalidated(event)
    return Announcement(text)


def announce_user_details_updated(
    event: UserDetailsUpdated, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a user's details have been changed."""
    text = user.assemble_text_for_user_details_updated(event)
    return Announcement(text)


def announce_user_account_suspended(
    event: UserAccountSuspended, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a user account has been suspended."""
    text = user.assemble_text_for_user_account_suspended(event)
    return Announcement(text)


def announce_user_account_unsuspended(
    event: UserAccountUnsuspended, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a user account has been unsuspended."""
    text = user.assemble_text_for_user_account_unsuspended(event)
    return Announcement(text)


def announce_user_account_deleted(
    event: UserAccountDeleted, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a user account has been deleted."""
    text = user.assemble_text_for_user_account_deleted(event)
    return Announcement(text)
