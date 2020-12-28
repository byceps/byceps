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

from ..helpers import get_screen_name_or_fallback

from ._config import CHANNEL_ORGA_LOG
from ._util import send_message


def announce_user_account_created(event: UserAccountCreated) -> None:
    """Announce that a user account has been created."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = (
        f'{initiator_screen_name} '
        f'hat das Benutzerkonto "{user_screen_name}" angelegt.'
    )

    send_user_message(event, CHANNEL_ORGA_LOG, text)


def announce_user_screen_name_changed(event: UserScreenNameChanged) -> None:
    """Announce that a user's screen name has been changed."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    text = (
        f'{initiator_screen_name} hat das Benutzerkonto '
        f'"{event.old_screen_name}" in "{event.new_screen_name}" umbenannt.'
    )

    send_user_message(event, CHANNEL_ORGA_LOG, text)


def announce_user_email_address_invalidated(
    event: UserEmailAddressInvalidated,
) -> None:
    """Announce that a user's email address has been invalidated."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = (
        f'{initiator_screen_name} hat die E-Mail-Adresse '
        f'des Benutzerkontos "{user_screen_name}" invalidiert.'
    )

    send_user_message(event, CHANNEL_ORGA_LOG, text)


def announce_user_details_updated_changed(event: UserDetailsUpdated) -> None:
    """Announce that a user's details have been changed."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = (
        f'{initiator_screen_name} hat die persönlichen Daten '
        f'des Benutzerkontos "{user_screen_name}" geändert.'
    )

    send_user_message(event, CHANNEL_ORGA_LOG, text)


def announce_user_account_suspended(event: UserAccountSuspended) -> None:
    """Announce that a user account has been suspended."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = (
        f'{initiator_screen_name} hat das Benutzerkonto '
        f'"{user_screen_name}" gesperrt.'
    )

    send_user_message(event, CHANNEL_ORGA_LOG, text)


def announce_user_account_unsuspended(event: UserAccountUnsuspended) -> None:
    """Announce that a user account has been unsuspended."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = (
        f'{initiator_screen_name} hat das Benutzerkonto '
        f'"{user_screen_name}" entsperrt.'
    )

    send_user_message(event, CHANNEL_ORGA_LOG, text)


def announce_user_account_deleted(event: UserAccountDeleted) -> None:
    """Announce that a user account has been created."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = (
        f'{initiator_screen_name} hat das Benutzerkonto '
        f'"{user_screen_name}" (ID "{event.user_id}") gelöscht.'
    )

    send_user_message(event, CHANNEL_ORGA_LOG, text)


# helpers


def send_user_message(event: _UserEvent, channel: str, text: str) -> None:
    scope = 'user'
    scope_id = None

    send_message(event, scope, scope_id, channel, text)
