"""
byceps.announce.handlers.page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce page events.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.page import PageCreated, PageDeleted, PageUpdated
from ...services.webhooks.transfer.models import OutgoingWebhook

from ..helpers import call_webhook
from ..text_assembly import page


def announce_page_created(event: PageCreated, webhook: OutgoingWebhook) -> None:
    """Announce that a page has been created."""
    text = page.assemble_text_for_page_created(event)

    call_webhook(webhook, text)


def announce_page_updated(event: PageUpdated, webhook: OutgoingWebhook) -> None:
    """Announce that a page has been updated."""
    text = page.assemble_text_for_page_updated(event)

    call_webhook(webhook, text)


def announce_page_deleted(event: PageDeleted, webhook: OutgoingWebhook) -> None:
    """Announce that a page has been deleted."""
    text = page.assemble_text_for_page_deleted(event)

    call_webhook(webhook, text)
