"""
byceps.announce.handlers.guest_server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce guest server events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask_babel import gettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.events.guest_server import GuestServerRegisteredEvent
from byceps.services.webhooks.models import Announcement, OutgoingWebhook


@with_locale
def announce_guest_server_registered(
    event_name: str, event: GuestServerRegisteredEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a guest server has been registered."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    owner_screen_name = get_screen_name_or_fallback(event.owner_screen_name)

    text = gettext(
        '%(initiator_screen_name)s has registered a guest server '
        'owned by "%(owner_screen_name)s for party "%(party_title)s".',
        initiator_screen_name=initiator_screen_name,
        owner_screen_name=owner_screen_name,
        party_title=event.party_title,
    )

    return Announcement(text)
