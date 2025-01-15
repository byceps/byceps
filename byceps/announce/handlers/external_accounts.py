"""
byceps.announce.handlers.external_accounts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce external account events.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.events.external_accounts import (
    ExternalAccountConnectedEvent,
    ExternalAccountDisconnectedEvent,
)
from byceps.services.webhooks.models import Announcement, OutgoingWebhook


@with_locale
def announce_external_account_connected(
    event_name: str,
    event: ExternalAccountConnectedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that an external account has been connected to a BYCEPS user account."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    user_screen_name = get_screen_name_or_fallback(event.user)

    text = gettext(
        '%(initiator_screen_name)s has connected an external account '
        'on "%(service)s" for %(user_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
        service=event.service,
    )

    return Announcement(text)


@with_locale
def announce_external_account_disconnected(
    event_name: str,
    event: ExternalAccountDisconnectedEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that an external account has been disconnected from a BYCEPS user account."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    user_screen_name = get_screen_name_or_fallback(event.user)

    text = gettext(
        '%(initiator_screen_name)s has disconnected an external account '
        'on "%(service)s" for %(user_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        user_screen_name=user_screen_name,
        service=event.service,
    )

    return Announcement(text)
