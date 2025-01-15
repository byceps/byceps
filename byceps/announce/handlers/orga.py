"""
byceps.announce.handlers.orga
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce orga events.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.events.orga import OrgaStatusGrantedEvent, OrgaStatusRevokedEvent
from byceps.services.webhooks.models import Announcement, OutgoingWebhook


@with_locale
def announce_orga_status_granted(
    event_name: str, event: OrgaStatusGrantedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that the orga status been granted to a user."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    user_screen_name = get_screen_name_or_fallback(event.user)

    text = gettext(
        '%(initiator_screen_name)s has granted orga status for brand %(brand_title)s to %(user_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        brand_title=event.brand.title,
        user_screen_name=user_screen_name,
    )

    return Announcement(text)


@with_locale
def announce_orga_status_revoked(
    event_name: str, event: OrgaStatusRevokedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that the orga status been revoked for a user."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    user_screen_name = get_screen_name_or_fallback(event.user)

    text = gettext(
        '%(initiator_screen_name)s has revoked orga status for brand %(brand_title)s for %(user_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        brand_title=event.brand.title,
        user_screen_name=user_screen_name,
    )

    return Announcement(text)
