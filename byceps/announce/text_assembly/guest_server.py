"""
byceps.announce.text_assembly.guest_server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce user badge events.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from ...events.guest_server import GuestServerRegistered

from ._helpers import get_screen_name_or_fallback, with_locale


@with_locale
def assemble_text_for_guest_server_registered(
    event: GuestServerRegistered,
) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    owner_screen_name = get_screen_name_or_fallback(event.owner_screen_name)

    return gettext(
        '%(initiator_screen_name)s has registered a guest server owned by "%(owner_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        owner_screen_name=owner_screen_name,
    )
