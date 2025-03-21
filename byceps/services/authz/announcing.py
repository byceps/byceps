"""
byceps.services.authz.announcing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce authorization events.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.services.webhooks.models import Announcement, OutgoingWebhook

from .events import RoleAssignedToUserEvent, RoleDeassignedFromUserEvent


@with_locale
def announce_role_assigned_to_user(
    event_name: str, event: RoleAssignedToUserEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a role has been assigned to a user."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    user_screen_name = get_screen_name_or_fallback(event.user)

    text = gettext(
        '%(initiator_screen_name)s has assigned role "%(role_id)s" to %(user_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        role_id=event.role_id,
        user_screen_name=user_screen_name,
    )

    return Announcement(text)


@with_locale
def announce_role_deassigned_from_user(
    event_name: str,
    event: RoleDeassignedFromUserEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that a role has been deassigned from a user."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    user_screen_name = get_screen_name_or_fallback(event.user)

    text = gettext(
        '%(initiator_screen_name)s has deassigned role "%(role_id)s" from %(user_screen_name)s.',
        initiator_screen_name=initiator_screen_name,
        role_id=event.role_id,
        user_screen_name=user_screen_name,
    )

    return Announcement(text)
