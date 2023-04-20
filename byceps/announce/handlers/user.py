"""
byceps.announce.handlers.user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce user events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations


from flask_babel import gettext

from byceps.announce.helpers import (
    Announcement,
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.events.user import (
    UserAccountCreated,
    UserAccountDeleted,
    UserAccountSuspended,
    UserAccountUnsuspended,
    UserDetailsUpdated,
    UserEmailAddressChanged,
    UserEmailAddressInvalidated,
    UserScreenNameChanged,
)
from byceps.services.site import site_service
from byceps.services.webhooks.models import OutgoingWebhook


@with_locale
def announce_user_account_created(
    event: UserAccountCreated, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a user account has been created."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    site = None
    if event.site_id:
        site = site_service.find_site(event.site_id)

    if site:
        text = gettext(
            '%(initiator_screen_name)s has created user account "%(user_screen_name)s" on site "%(site_title)s".',
            initiator_screen_name=initiator_screen_name,
            user_screen_name=user_screen_name,
            site_title=site.title,
        )
    else:
        text = gettext(
            '%(initiator_screen_name)s has created user account "%(user_screen_name)s".',
            initiator_screen_name=initiator_screen_name,
            user_screen_name=user_screen_name,
        )

    return Announcement(text)


@with_locale
def announce_user_screen_name_changed(
    event: UserScreenNameChanged, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a user's screen name has been changed."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    old_screen_name = get_screen_name_or_fallback(event.old_screen_name)
    new_screen_name = get_screen_name_or_fallback(event.new_screen_name)

    text = gettext(
        '%(initiator_screen_name)s has renamed user account "%(old_screen_name)s" to "%(new_screen_name)s".',
        initiator_screen_name=initiator_screen_name,
        old_screen_name=old_screen_name,
        new_screen_name=new_screen_name,
    )

    return Announcement(text)


@with_locale
def announce_user_email_address_changed(
    event: UserEmailAddressChanged, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a user's email address has been changed."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = gettext(
        '%(initiator_screen_name)s has changed the email address of user account "%(user_screen_name)s".',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
    )

    return Announcement(text)


@with_locale
def announce_user_email_address_invalidated(
    event: UserEmailAddressInvalidated, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a user's email address has been invalidated."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = gettext(
        '%(initiator_screen_name)s has invalidated the email address of user account "%(user_screen_name)s".',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
    )

    return Announcement(text)


@with_locale
def announce_user_details_updated(
    event: UserDetailsUpdated, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a user's details have been changed."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = gettext(
        '%(initiator_screen_name)s has changed personal data of user account "%(user_screen_name)s".',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
    )

    return Announcement(text)


@with_locale
def announce_user_account_suspended(
    event: UserAccountSuspended, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a user account has been suspended."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = gettext(
        '%(initiator_screen_name)s has suspended user account "%(user_screen_name)s".',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
    )

    return Announcement(text)


@with_locale
def announce_user_account_unsuspended(
    event: UserAccountUnsuspended, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a user account has been unsuspended."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = gettext(
        '%(initiator_screen_name)s has unsuspended user account "%(user_screen_name)s".',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
    )

    return Announcement(text)


@with_locale
def announce_user_account_deleted(
    event: UserAccountDeleted, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a user account has been deleted."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = gettext(
        '%(initiator_screen_name)s has deleted user account "%(user_screen_name)s" (ID "%(user_id)s").',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
        user_id=event.user_id,
    )

    return Announcement(text)
