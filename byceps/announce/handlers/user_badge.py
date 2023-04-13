"""
byceps.announce.handlers.user_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce user badge events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...events.user_badge import UserBadgeAwarded
from ...services.webhooks.models import OutgoingWebhook

from ..helpers import Announcement
from ..text_assembly import user_badge


def announce_user_badge_awarded(
    event: UserBadgeAwarded, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a badge has been awarded to a user."""
    text = user_badge.assemble_text_for_user_badge_awarded(event)
    return Announcement(text)
