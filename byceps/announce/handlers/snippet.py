"""
byceps.announce.handlers.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce snippet events.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.snippet import (
    _SnippetEvent,
    SnippetCreated,
    SnippetDeleted,
    SnippetUpdated,
)
from ...services.webhooks.transfer.models import OutgoingWebhook

from ..common import snippet
from ..helpers import call_webhook


def announce_snippet_created(
    event: SnippetCreated, webhook: OutgoingWebhook
) -> None:
    """Announce that a snippet has been created."""
    text = snippet.assemble_text_for_snippet_created(event)

    send_snippet_message(event, webhook, text)


def announce_snippet_updated(
    event: SnippetUpdated, webhook: OutgoingWebhook
) -> None:
    """Announce that a snippet has been updated."""
    text = snippet.assemble_text_for_snippet_updated(event)

    send_snippet_message(event, webhook, text)


def announce_snippet_deleted(
    event: SnippetDeleted, webhook: OutgoingWebhook
) -> None:
    """Announce that a snippet has been deleted."""
    text = snippet.assemble_text_for_snippet_deleted(event)

    send_snippet_message(event, webhook, text)


# helpers


def send_snippet_message(
    event: _SnippetEvent, webhook: OutgoingWebhook, text: str
) -> None:
    call_webhook(webhook, text)
