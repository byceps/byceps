"""
byceps.announce.irc.user
~~~~~~~~~~~~~~~~~~~~~~~~

Announce user events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...events.user import (
    UserAccountCreated,
    UserAccountDeleted,
    UserAccountSuspended,
    UserAccountUnsuspended,
    UserDetailsUpdated,
    UserEmailAddressInvalidated,
    UserScreenNameChanged,
)
from ...services.user import service as user_service
from ...signals import user as user_signals
from ...typing import UserID
from ...util.irc import send_message
from ...util.jobqueue import enqueue

from ..helpers import get_screen_name_or_fallback

from ._config import CHANNEL_ORGA_LOG


@user_signals.account_created.connect
def _on_user_account_created(sender, *, event: UserAccountCreated) -> None:
    enqueue(announce_user_account_created, event)


def announce_user_account_created(event: UserAccountCreated) -> None:
    """Announce that a user account has been created."""
    channels = [CHANNEL_ORGA_LOG]

    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = _get_screen_name(event.user_id)

    text = (
        f'{initiator_screen_name} '
        f'hat das Benutzerkonto "{user_screen_name}" angelegt.'
    )

    send_message(channels, text)


@user_signals.screen_name_changed.connect
def _on_user_screen_name_changed(
    sender, *, event: UserScreenNameChanged
) -> None:
    enqueue(announce_user_screen_name_changed, event)


def announce_user_screen_name_changed(event: UserScreenNameChanged) -> None:
    """Announce that a user's screen name has been changed."""
    channels = [CHANNEL_ORGA_LOG]

    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    text = (
        f'{initiator_screen_name} hat das Benutzerkonto '
        f'"{event.old_screen_name}" in "{event.new_screen_name}" umbenannt.'
    )

    send_message(channels, text)


@user_signals.email_address_invalidated.connect
def _on_user_email_address_invalidated(
    sender, *, event: UserEmailAddressInvalidated
) -> None:
    enqueue(announce_user_email_address_invalidated, event)


def announce_user_email_address_invalidated(
    event: UserEmailAddressInvalidated,
) -> None:
    """Announce that a user's email address has been invalidated."""
    channels = [CHANNEL_ORGA_LOG]

    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = _get_screen_name(event.user_id)

    text = (
        f'{initiator_screen_name} hat die E-Mail-Adresse '
        f'des Benutzerkontos "{user_screen_name}" invalidiert.'
    )

    send_message(channels, text)


@user_signals.details_updated.connect
def _on_user_details_updated_changed(
    sender, *, event: UserDetailsUpdated
) -> None:
    enqueue(announce_user_details_updated_changed, event)


def announce_user_details_updated_changed(event: UserDetailsUpdated) -> None:
    """Announce that a user's details have been changed."""
    channels = [CHANNEL_ORGA_LOG]

    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = _get_screen_name(event.user_id)

    text = (
        f'{initiator_screen_name} hat die persönlichen Daten '
        f'des Benutzerkontos "{user_screen_name}" geändert.'
    )

    send_message(channels, text)


@user_signals.account_suspended.connect
def _on_user_account_suspended(sender, *, event: UserAccountSuspended) -> None:
    enqueue(announce_user_account_suspended, event)


def announce_user_account_suspended(event: UserAccountSuspended) -> None:
    """Announce that a user account has been suspended."""
    channels = [CHANNEL_ORGA_LOG]

    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = _get_screen_name(event.user_id)

    text = (
        f'{initiator_screen_name} hat das Benutzerkonto '
        f'"{user_screen_name}" gesperrt.'
    )

    send_message(channels, text)


@user_signals.account_unsuspended.connect
def _on_user_account_unsuspended(
    sender, *, event: UserAccountUnsuspended
) -> None:
    enqueue(announce_user_account_unsuspended, event)


def announce_user_account_unsuspended(event: UserAccountUnsuspended) -> None:
    """Announce that a user account has been unsuspended."""
    channels = [CHANNEL_ORGA_LOG]

    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = _get_screen_name(event.user_id)

    text = (
        f'{initiator_screen_name} hat das Benutzerkonto '
        f'"{user_screen_name}" entsperrt.'
    )

    send_message(channels, text)


@user_signals.account_deleted.connect
def _on_user_account_deleted(sender, *, event: UserAccountDeleted) -> None:
    enqueue(announce_user_account_deleted, event)


def announce_user_account_deleted(event: UserAccountDeleted) -> None:
    """Announce that a user account has been created."""
    channels = [CHANNEL_ORGA_LOG]

    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user = user_service.get_user(event.user_id)

    text = (
        f'{initiator_screen_name} hat das Benutzerkonto '
        f'mit der ID "{user.id}" gelöscht.'
    )

    send_message(channels, text)


def _get_screen_name(user_id: UserID) -> str:
    screen_name = user_service.find_screen_name(user_id)
    return get_screen_name_or_fallback(screen_name)
