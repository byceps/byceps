"""
byceps.announce.handlers.user_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce user badge events.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.services.user_badge.events import UserBadgeAwardedEvent
from byceps.services.webhooks.models import Announcement, OutgoingWebhook


@with_locale
def announce_user_badge_awarded(
    event_name: str, event: UserBadgeAwardedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a badge has been awarded to a user."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    awardee_screen_name = get_screen_name_or_fallback(event.awardee)

    text = gettext(
        '%(initiator_screen_name)s has awarded badge "%(badge_label)s" to %(awardee_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        badge_label=event.badge_label,
        awardee_screen_name=awardee_screen_name,
    )

    return Announcement(text)
