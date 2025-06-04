"""
byceps.services.newsletter.announcing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce newsletter events.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.services.webhooks.models import Announcement, OutgoingWebhook

from .events import SubscribedToNewsletterEvent, UnsubscribedFromNewsletterEvent


@with_locale
def announce_subscribed_to_newsletter(
    event_name: str,
    event: SubscribedToNewsletterEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that someone has subscribed to a newsletter."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    user_screen_name = get_screen_name_or_fallback(event.user)

    if event.initiator != event.user:
        text = gettext(
            '%(initiator_screen_name)s has subscribed %(user_screen_name)s to newsletter "%(list_title)s".',
            initiator_screen_name=initiator_screen_name,
            user_screen_name=user_screen_name,
            list_title=event.list_title,
        )
    else:
        text = gettext(
            '%(user_screen_name)s has subscribed to newsletter "%(list_title)s".',
            user_screen_name=user_screen_name,
            list_title=event.list_title,
        )

    return Announcement(text)


@with_locale
def announce_unsubscribed_from_newsletter(
    event_name: str,
    event: UnsubscribedFromNewsletterEvent,
    webhook: OutgoingWebhook,
) -> Announcement | None:
    """Announce that someone has unsubscribed from a newsletter."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)
    user_screen_name = get_screen_name_or_fallback(event.user)

    if event.initiator != event.user:
        text = gettext(
            '%(initiator_screen_name)s has unsubscribed %(user_screen_name)s from newsletter "%(list_title)s".',
            initiator_screen_name=initiator_screen_name,
            user_screen_name=user_screen_name,
            list_title=event.list_title,
        )
    else:
        text = gettext(
            '%(user_screen_name)s has unsubscribed from newsletter "%(list_title)s".',
            user_screen_name=user_screen_name,
            list_title=event.list_title,
        )

    return Announcement(text)
