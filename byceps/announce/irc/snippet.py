"""
byceps.announce.irc.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce snippet events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...events.snippet import SnippetCreated, SnippetDeleted, SnippetUpdated
from ...services.snippet.transfer.models import SnippetType
from ...signals import snippet as snippet_signals
from ...util.irc import send_message
from ...util.jobqueue import enqueue

from ..helpers import get_screen_name_or_fallback

from ._config import CHANNEL_ORGA_LOG


@snippet_signals.snippet_created.connect
def _on_snippet_created(sender, *, event: SnippetCreated = None) -> None:
    enqueue(announce_snippet_created, event)


def announce_snippet_created(event: SnippetCreated) -> None:
    """Announce that a snippet has been created."""
    editor_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    type_label = _get_snippet_type_label(event.snippet_type)

    text = (
        f'{editor_screen_name} hat das Snippet-{type_label} '
        f'"{event.snippet_name}" im Scope '
        f'"{event.scope.type_}/{event.scope.name}" angelegt.'
    )

    send_message(CHANNEL_ORGA_LOG, text)


@snippet_signals.snippet_updated.connect
def _on_snippet_updated(sender, *, event: SnippetUpdated = None) -> None:
    enqueue(announce_snippet_updated, event)


def announce_snippet_updated(event: SnippetUpdated) -> None:
    """Announce that a snippet has been updated."""
    editor_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    type_label = _get_snippet_type_label(event.snippet_type)

    text = (
        f'{editor_screen_name} hat das Snippet-{type_label} '
        f'"{event.snippet_name}" im Scope '
        f'"{event.scope.type_}/{event.scope.name}" aktualisiert.'
    )

    send_message(CHANNEL_ORGA_LOG, text)


@snippet_signals.snippet_deleted.connect
def _on_snippet_deleted(sender, *, event: SnippetDeleted = None) -> None:
    enqueue(announce_snippet_deleted, event)


def announce_snippet_deleted(event: SnippetDeleted) -> None:
    """Announce that a snippet has been deleted."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    text = (
        f'{initiator_screen_name} hat das Snippet "{event.snippet_name}" '
        f'im Scope "{event.scope.type_}/{event.scope.name}" gelöscht.'
    )

    send_message(CHANNEL_ORGA_LOG, text)


_SNIPPET_TYPE_LABELS = {
    SnippetType.document: 'Dokument',
    SnippetType.fragment: 'Fragment',
}


def _get_snippet_type_label(snippet_type: SnippetType) -> str:
    """Return label for snippet type."""
    return _SNIPPET_TYPE_LABELS.get(snippet_type, '?')
