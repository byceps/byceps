"""
byceps.announce.handlers.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce snippet events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.snippet import SnippetCreated, SnippetDeleted, SnippetUpdated
from ...services.webhooks.models import OutgoingWebhook

from ..helpers import call_webhook
from ..text_assembly import snippet


def announce_snippet_created(
    event: SnippetCreated, webhook: OutgoingWebhook
) -> None:
    """Announce that a snippet has been created."""
    text = snippet.assemble_text_for_snippet_created(event)

    call_webhook(webhook, text)


def announce_snippet_updated(
    event: SnippetUpdated, webhook: OutgoingWebhook
) -> None:
    """Announce that a snippet has been updated."""
    text = snippet.assemble_text_for_snippet_updated(event)

    call_webhook(webhook, text)


def announce_snippet_deleted(
    event: SnippetDeleted, webhook: OutgoingWebhook
) -> None:
    """Announce that a snippet has been deleted."""
    text = snippet.assemble_text_for_snippet_deleted(event)

    call_webhook(webhook, text)
