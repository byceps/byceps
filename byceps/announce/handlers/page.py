"""
byceps.announce.handlers.page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce page events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

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
    event_name: str, event: PageCreatedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a page has been created."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)

    text = gettext(
        '%(initiator_screen_name)s has created page "%(page_name)s" (%(language_code)s) in site "%(site_title)s".',
        initiator_screen_name=initiator_screen_name,
        page_name=event.page_name,
        language_code=event.language_code,
        site_title=event.site.title,
    )

    return Announcement(text)


@with_locale
def announce_page_updated(
    event_name: str, event: PageUpdatedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a page has been updated."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)

    text = gettext(
        '%(initiator_screen_name)s has updated page "%(page_name)s" (%(language_code)s) in site "%(site_title)s".',
        initiator_screen_name=initiator_screen_name,
        page_name=event.page_name,
        language_code=event.language_code,
        site_title=event.site.title,
    )

    return Announcement(text)


@with_locale
def announce_page_deleted(
    event_name: str, event: PageDeletedEvent, webhook: OutgoingWebhook
) -> Announcement | None:
    """Announce that a page has been deleted."""
    initiator_screen_name = get_screen_name_or_fallback(event.initiator)

    text = gettext(
        '%(initiator_screen_name)s has deleted page "%(page_name)s" (%(language_code)s) in site "%(site_title)s".',
        initiator_screen_name=initiator_screen_name,
        page_name=event.page_name,
        language_code=event.language_code,
        site_title=event.site.title,
    )

    return Announcement(text)
