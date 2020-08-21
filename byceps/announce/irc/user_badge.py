"""
byceps.announce.irc.user_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce user badge events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...events.user_badge import UserBadgeAwarded
from ...services.user import service as user_service
from ...signals import user_badge as user_badge_signals
from ...util.irc import send_message
from ...util.jobqueue import enqueue

from ._config import CHANNEL_ORGA_LOG, CHANNEL_PUBLIC


@user_badge_signals.user_badge_awarded.connect
def _on_user_badge_awarded(sender, *, event: UserBadgeAwarded) -> None:
    enqueue(announce_user_badge_awarded, event)


def announce_user_badge_awarded(event: UserBadgeAwarded) -> None:
    """Announce that a badge has been awarded to a user."""
    channels = [CHANNEL_ORGA_LOG]

    user = user_service.get_user(event.user_id)

    if event.initiator_id:
        initiator = user_service.get_user(event.initiator_id)
        initiator_name = initiator.screen_name
    else:
        initiator_name = 'Jemand'

    text = (
        f'{initiator_name} hat das Abzeichen "{event.badge_label}" '
        f'an {user.screen_name} verliehen.'
    )

    send_message(channels, text)
