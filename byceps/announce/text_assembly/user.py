"""
byceps.announce.text_assembly.user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce user events.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

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
from ...services.site import service as site_service

from ._helpers import get_screen_name_or_fallback, with_locale


@with_locale
def assemble_text_for_user_account_created(event: UserAccountCreated) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    site = None
    if event.site_id:
        site = site_service.find_site(event.site_id)

    if site:
        return gettext(
            '%(initiator_screen_name)s has created user account "%(user_screen_name)s" on site "%(site_title)s".',
            initiator_screen_name=initiator_screen_name,
            user_screen_name=user_screen_name,
            site_title=site.title,
        )
    else:
        return gettext(
            '%(initiator_screen_name)s has created user account "%(user_screen_name)s".',
            initiator_screen_name=initiator_screen_name,
            user_screen_name=user_screen_name,
        )


@with_locale
def assemble_text_for_user_screen_name_changed(
    event: UserScreenNameChanged,
) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    return gettext(
        '%(initiator_screen_name)s has renamed user account "%(old_screen_name)s" to "%(new_screen_name)s".',
        initiator_screen_name=initiator_screen_name,
        old_screen_name=event.old_screen_name,
        new_screen_name=event.new_screen_name,
    )


@with_locale
def assemble_text_for_user_email_address_changed(
    event: UserEmailAddressChanged,
) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return gettext(
        '%(initiator_screen_name)s has changed the email address of user account "%(user_screen_name)s".',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
    )


@with_locale
def assemble_text_for_user_email_address_invalidated(
    event: UserEmailAddressInvalidated,
) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return gettext(
        '%(initiator_screen_name)s has invalidated the email address of user account "%(user_screen_name)s".',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
    )


@with_locale
def assemble_text_for_user_details_updated(event: UserDetailsUpdated) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return gettext(
        '%(initiator_screen_name)s has changed personal data of user account "%(user_screen_name)s".',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
    )


@with_locale
def assemble_text_for_user_account_suspended(
    event: UserAccountSuspended,
) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return gettext(
        '%(initiator_screen_name)s has suspended user account "%(user_screen_name)s".',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
    )


@with_locale
def assemble_text_for_user_account_unsuspended(
    event: UserAccountUnsuspended,
) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return gettext(
        '%(initiator_screen_name)s has unsuspended user account "%(user_screen_name)s".',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
    )


@with_locale
def assemble_text_for_user_account_deleted(event: UserAccountDeleted) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return gettext(
        '%(initiator_screen_name)s has deleted user account "%(user_screen_name)s" (ID "%(user_id)s").',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
        user_id=event.user_id,
    )
