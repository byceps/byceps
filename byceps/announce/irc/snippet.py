"""
byceps.announce.irc.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce snippet events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.snippet import (
    _SnippetEvent,
    SnippetCreated,
    SnippetDeleted,
    SnippetUpdated,
)

from ..common import snippet
from ..helpers import send_message


def announce_snippet_created(
    event: SnippetCreated, webhook_format: str
) -> None:
    """Announce that a snippet has been created."""
    text = snippet.assemble_text_for_snippet_created(event)

    send_snippet_message(event, webhook_format, text)


def announce_snippet_updated(
    event: SnippetUpdated, webhook_format: str
) -> None:
    """Announce that a snippet has been updated."""
    text = snippet.assemble_text_for_snippet_updated(event)

    send_snippet_message(event, webhook_format, text)


def announce_snippet_deleted(
    event: SnippetDeleted, webhook_format: str
) -> None:
    """Announce that a snippet has been deleted."""
    text = snippet.assemble_text_for_snippet_deleted(event)

    send_snippet_message(event, webhook_format, text)


# helpers


def send_snippet_message(
    event: _SnippetEvent, webhook_format: str, text: str
) -> None:
    scope = 'snippet'
    scope_id = None

    send_message(event, webhook_format, scope, scope_id, text)
