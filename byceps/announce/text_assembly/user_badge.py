"""
byceps.announce.text_assembly.user_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce user badge events.

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from ...events.user_badge import UserBadgeAwarded

from ._helpers import get_screen_name_or_fallback, with_locale


@with_locale
def assemble_text_for_user_badge_awarded(event: UserBadgeAwarded) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    awardee_screen_name = get_screen_name_or_fallback(event.user_screen_name)

    return gettext(
        '%(initiator_screen_name)s has awarded badge "%(badge_label)s" to %(awardee_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        badge_label=event.badge_label,
        awardee_screen_name=awardee_screen_name,
    )
