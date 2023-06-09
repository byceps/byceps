"""
byceps.announce.handlers.user_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce user badge events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask_babel import gettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.events.user_badge import UserBadgeAwardedEvent
from byceps.services.webhooks.models import Announcement, OutgoingWebhook


@with_locale
def announce_user_badge_awarded(
    event: UserBadgeAwardedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a badge has been awarded to a user."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    awardee_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = gettext(
        '%(initiator_screen_name)s has awarded badge "%(badge_label)s" to %(awardee_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        badge_label=event.badge_label,
        awardee_screen_name=awardee_screen_name,
    )

    return Announcement(text)
