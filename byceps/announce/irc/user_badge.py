"""
byceps.announce.irc.user_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce user badge events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...events.user_badge import UserBadgeAwarded
from ...signals import user_badge as user_badge_signals
from ...util.jobqueue import enqueue

from ..helpers import get_screen_name_or_fallback

from ._config import CHANNEL_ORGA_LOG
from ._util import send_message


@user_badge_signals.user_badge_awarded.connect
def _on_user_badge_awarded(
    sender, *, event: Optional[UserBadgeAwarded] = None
) -> None:
    enqueue(announce_user_badge_awarded, event)


def announce_user_badge_awarded(event: UserBadgeAwarded) -> None:
    """Announce that a badge has been awarded to a user."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    awardee_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    text = (
        f'{initiator_screen_name} hat das Abzeichen "{event.badge_label}" '
        f'an {awardee_screen_name} verliehen.'
    )

    send_message(CHANNEL_ORGA_LOG, text)
