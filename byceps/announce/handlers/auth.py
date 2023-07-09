"""
byceps.announce.handlers.auth
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce auth events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask_babel import gettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.events.auth import PasswordUpdatedEvent, UserLoggedInEvent
from byceps.services.webhooks.models import Announcement, OutgoingWebhook


@with_locale
def announce_password_updated(
    event_name: str, event: PasswordUpdatedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that an account password was updated."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    user_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = gettext(
        '%(initiator_screen_name)s has updated the password for %(user_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
    )

    return Announcement(text)


@with_locale
def announce_user_logged_in(
    event_name: str, event: UserLoggedInEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a user has logged in."""
    screen_name = get_screen_name_or_fallback(event.initiator_screen_name)

    if event.site_id:
        text = gettext(
            '%(screen_name)s has logged in on site "%(site_title)s".',
            screen_name=screen_name,
            site_title=event.site_title,
        )
    else:
        text = gettext(
            '%(screen_name)s has logged in.', screen_name=screen_name
        )

    return Announcement(text)
