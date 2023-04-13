"""
byceps.announce.handlers.auth
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce auth events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from flask_babel import gettext

from ...events.auth import UserLoggedIn
from ...services.site import site_service
from ...services.webhooks.models import OutgoingWebhook

from ..helpers import Announcement, get_screen_name_or_fallback, with_locale


@with_locale
def announce_user_logged_in(
    event: UserLoggedIn, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a user has logged in."""
    screen_name = get_screen_name_or_fallback(event.initiator_screen_name)

    site = None
    if event.site_id:
        site = site_service.find_site(event.site_id)

    if site:
        text = gettext(
            '%(screen_name)s has logged in on site "%(site_title)s".',
            screen_name=screen_name,
            site_title=site.title,
        )
    else:
        text = gettext(
            '%(screen_name)s has logged in.', screen_name=screen_name
        )

    return Announcement(text)
