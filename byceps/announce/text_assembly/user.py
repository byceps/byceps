"""
byceps.announce.text_assembly.user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce user events.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
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

from ._helpers import get_screen_name_or_fallback


def assemble_text_for_user_account_created(event: UserAccountCreated) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return (
        f'{initiator_screen_name} '
        f'hat das Benutzerkonto "{user_screen_name}" angelegt.'
    )


def assemble_text_for_user_screen_name_changed(
    event: UserScreenNameChanged,
) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    return (
        f'{initiator_screen_name} hat das Benutzerkonto '
        f'"{event.old_screen_name}" in "{event.new_screen_name}" umbenannt.'
    )


def assemble_text_for_user_email_address_invalidated(
    event: UserEmailAddressInvalidated,
) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return (
        f'{initiator_screen_name} hat die E-Mail-Adresse '
        f'des Benutzerkontos "{user_screen_name}" invalidiert.'
    )


def assemble_text_for_user_details_updated_changed(
    event: UserDetailsUpdated,
) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return (
        f'{initiator_screen_name} hat die persönlichen Daten '
        f'des Benutzerkontos "{user_screen_name}" geändert.'
    )


def assemble_text_for_user_account_suspended(
    event: UserAccountSuspended,
) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return (
        f'{initiator_screen_name} hat das Benutzerkonto '
        f'"{user_screen_name}" gesperrt.'
    )


def assemble_text_for_user_account_unsuspended(
    event: UserAccountUnsuspended,
) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return (
        f'{initiator_screen_name} hat das Benutzerkonto '
        f'"{user_screen_name}" entsperrt.'
    )


def assemble_text_for_user_account_deleted(event: UserAccountDeleted) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return (
        f'{initiator_screen_name} hat das Benutzerkonto '
        f'"{user_screen_name}" (ID "{event.user_id}") gelöscht.'
    )
