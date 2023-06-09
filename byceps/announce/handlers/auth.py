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
from byceps.events.auth import UserLoggedInEvent
from byceps.services.webhooks.models import Announcement, OutgoingWebhook


@with_locale
def announce_user_logged_in(
    event: UserLoggedInEvent, webhook: OutgoingWebhook
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
