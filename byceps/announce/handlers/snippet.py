"""
byceps.announce.handlers.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce snippet events.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.snippet import SnippetCreated, SnippetDeleted, SnippetUpdated
from ...services.webhooks.transfer.models import OutgoingWebhook

from ..helpers import call_webhook
from ..text_assembly import snippet


def announce_snippet_created(
    event: SnippetCreated, webhook: OutgoingWebhook
) -> None:
    """Announce that a snippet has been created."""
    text = snippet.assemble_text_for_snippet_created(event)

    send_snippet_message(webhook, text)


def announce_snippet_updated(
    event: SnippetUpdated, webhook: OutgoingWebhook
) -> None:
    """Announce that a snippet has been updated."""
    text = snippet.assemble_text_for_snippet_updated(event)

    send_snippet_message(webhook, text)


def announce_snippet_deleted(
    event: SnippetDeleted, webhook: OutgoingWebhook
) -> None:
    """Announce that a snippet has been deleted."""
    text = snippet.assemble_text_for_snippet_deleted(event)

    send_snippet_message(webhook, text)


# helpers


def send_snippet_message(webhook: OutgoingWebhook, text: str) -> None:
    call_webhook(webhook, text)
