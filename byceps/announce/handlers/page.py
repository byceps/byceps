"""
byceps.announce.handlers.page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce page events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...events.page import PageCreated, PageDeleted, PageUpdated
from ...services.webhooks.models import OutgoingWebhook

from ..helpers import Announcement
from ..text_assembly import page


def announce_page_created(
    event: PageCreated, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a page has been created."""
    text = page.assemble_text_for_page_created(event)
    return Announcement(text)


def announce_page_updated(
    event: PageUpdated, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a page has been updated."""
    text = page.assemble_text_for_page_updated(event)
    return Announcement(text)


def announce_page_deleted(
    event: PageDeleted, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a page has been deleted."""
    text = page.assemble_text_for_page_deleted(event)
    return Announcement(text)
