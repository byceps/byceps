"""
byceps.announce.handlers.page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce page events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask_babel import gettext

from byceps.announce.helpers import (
    get_screen_name_or_fallback,
    with_locale,
)
from byceps.events.page import (
    PageCreatedEvent,
    PageDeletedEvent,
    PageUpdatedEvent,
)
from byceps.services.webhooks.models import Announcement, OutgoingWebhook


@with_locale
def announce_page_created(
    event: PageCreatedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a page has been created."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    text = gettext(
        '%(initiator_screen_name)s has created page "%(page_name)s" in site "%(site_id)s".',
        initiator_screen_name=initiator_screen_name,
        page_name=event.page_name,
        site_id=event.site_id,
    )

    return Announcement(text)


@with_locale
def announce_page_updated(
    event: PageUpdatedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a page has been updated."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    text = gettext(
        '%(initiator_screen_name)s has updated page "%(page_name)s" in site "%(site_id)s".',
        initiator_screen_name=initiator_screen_name,
        page_name=event.page_name,
        site_id=event.site_id,
    )

    return Announcement(text)


@with_locale
def announce_page_deleted(
    event: PageDeletedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a page has been deleted."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    text = gettext(
        '%(initiator_screen_name)s has deleted page "%(page_name)s" in site "%(site_id)s".',
        initiator_screen_name=initiator_screen_name,
        page_name=event.page_name,
        site_id=event.site_id,
    )

    return Announcement(text)
