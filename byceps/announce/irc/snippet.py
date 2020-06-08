"""
byceps.announce.irc.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce snippet events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...blueprints.snippet import signals
from ...events.snippet import SnippetCreated, SnippetUpdated
from ...services.snippet import service as snippet_service
from ...util.irc import send_message
from ...util.jobqueue import enqueue

from ._config import CHANNEL_ORGA_LOG, CHANNEL_PUBLIC


@signals.snippet_created.connect
def _on_snippet_created(sender, *, event: SnippetCreated = None) -> None:
    enqueue(announce_snippet_created, event)


def announce_snippet_created(event: SnippetCreated) -> None:
    """Announce that a snippet has been created."""
    channels = [CHANNEL_ORGA_LOG]

    snippet_version = snippet_service.find_snippet_version(
        event.snippet_version_id
    )
    snippet = snippet_version.snippet
    editor = snippet_version.creator
    type_name = 'Dokument' if snippet.is_document else 'Fragment'

    text = (
        f'{editor.screen_name} hat das Snippet-{type_name} '
        f'"{snippet.name}" im Scope '
        f'"{snippet.scope.type_}/{snippet.scope.name}" angelegt.'
    )

    send_message(channels, text)


@signals.snippet_updated.connect
def _on_snippet_updated(sender, *, event: SnippetUpdated = None) -> None:
    enqueue(announce_snippet_updated, event)


def announce_snippet_updated(event: SnippetUpdated = None) -> None:
    """Announce that a snippet has been updated."""
    channels = [CHANNEL_ORGA_LOG]

    snippet_version = snippet_service.find_snippet_version(
        event.snippet_version_id
    )
    snippet = snippet_version.snippet
    editor = snippet_version.creator
    type_name = 'Dokument' if snippet.is_document else 'Fragment'

    text = (
        f'{editor.screen_name} hat das Snippet-{type_name} '
        f'"{snippet.name}" im Scope '
        f'"{snippet.scope.type_}/{snippet.scope.name}" aktualisiert.'
    )

    send_message(channels, text)
