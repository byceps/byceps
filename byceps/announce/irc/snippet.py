"""
byceps.announce.irc.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce snippet events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...events.snippet import SnippetCreated, SnippetDeleted, SnippetUpdated
from ...services.snippet import service as snippet_service
from ...services.user import service as user_service
from ...signals import snippet as snippet_signals
from ...util.irc import send_message
from ...util.jobqueue import enqueue

from ._config import CHANNEL_ORGA_LOG, CHANNEL_PUBLIC


@snippet_signals.snippet_created.connect
def _on_snippet_created(sender, *, event: SnippetCreated = None) -> None:
    enqueue(announce_snippet_created, event)


def announce_snippet_created(event: SnippetCreated) -> None:
    """Announce that a snippet has been created."""
    channels = [CHANNEL_ORGA_LOG]

    snippet_version = snippet_service.find_snippet_version(
        event.snippet_version_id
    )
    snippet = snippet_version.snippet
    editor_screen_name = user_service.find_screen_name(event.initiator_id)
    type_name = 'Dokument' if snippet.is_document else 'Fragment'

    text = (
        f'{editor_screen_name} hat das Snippet-{type_name} '
        f'"{snippet.name}" im Scope '
        f'"{snippet.scope.type_}/{snippet.scope.name}" angelegt.'
    )

    send_message(channels, text)


@snippet_signals.snippet_updated.connect
def _on_snippet_updated(sender, *, event: SnippetUpdated = None) -> None:
    enqueue(announce_snippet_updated, event)


def announce_snippet_updated(event: SnippetUpdated) -> None:
    """Announce that a snippet has been updated."""
    channels = [CHANNEL_ORGA_LOG]

    snippet_version = snippet_service.find_snippet_version(
        event.snippet_version_id
    )
    snippet = snippet_version.snippet
    editor_screen_name = user_service.find_screen_name(event.initiator_id)
    type_name = 'Dokument' if snippet.is_document else 'Fragment'

    text = (
        f'{editor_screen_name} hat das Snippet-{type_name} '
        f'"{snippet.name}" im Scope '
        f'"{snippet.scope.type_}/{snippet.scope.name}" aktualisiert.'
    )

    send_message(channels, text)


@snippet_signals.snippet_deleted.connect
def _on_snippet_deleted(sender, *, event: SnippetDeleted = None) -> None:
    enqueue(announce_snippet_deleted, event)


def announce_snippet_deleted(event: SnippetDeleted) -> None:
    """Announce that a snippet has been deleted."""
    channels = [CHANNEL_ORGA_LOG]

    initiator_screen_name = user_service.find_screen_name(event.initiator_id)

    text = (
        f'{initiator_screen_name} hat das Snippet "{event.snippet_name}" '
        f'im Scope "{event.scope.type_}/{event.scope.name}" gelöscht.'
    )

    send_message(channels, text)
