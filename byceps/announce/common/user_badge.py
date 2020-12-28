"""
byceps.announce.common.user_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce user badge events.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.user_badge import UserBadgeAwarded

from ..helpers import get_screen_name_or_fallback


def assemble_text_for_user_badge_awarded(event: UserBadgeAwarded) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    awardee_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return (
        f'{initiator_screen_name} hat das Abzeichen "{event.badge_label}" '
        f'an {awardee_screen_name} verliehen.'
    )
