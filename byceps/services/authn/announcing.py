"""
byceps.services.authn.announcing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce authentication events.

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.services.webhooks.models import Announcement, OutgoingWebhook

from .events import (
    PasswordUpdatedEvent,
    UserLoggedInToAdminEvent,
    UserLoggedInToSiteEvent,
)


@with_locale
def announce_password_updated(
    event_name: str, event: PasswordUpdatedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that an account password was updated."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    user_screen_name = get_screen_name_or_fallback(event.user)

    text = gettext(
        '%(initiator_screen_name)s has updated the password for %(user_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
    )

    return Announcement(text)


@with_locale
def announce_user_logged_in_to_admin(
    event_name: str, event: UserLoggedInToAdminEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a user has logged in to administration."""
    screen_name = get_screen_name_or_fallback(event.user)

    text = gettext(
        '%(screen_name)s has logged in to administration.',
        screen_name=screen_name,
    )

    return Announcement(text)


@with_locale
def announce_user_logged_in_to_site(
    event_name: str, event: UserLoggedInToSiteEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a user has logged in to a site."""
    screen_name = get_screen_name_or_fallback(event.user)

    text = gettext(
        '%(screen_name)s has logged in to site "%(site_title)s".',
        screen_name=screen_name,
        site_title=event.site.title,
    )

    return Announcement(text)
