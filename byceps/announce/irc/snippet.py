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
from ...services.snippet.transfer.models import SnippetType

from ..helpers import get_screen_name_or_fallback

from ._util import send_message


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

    send_snippet_message(event, text)


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

    send_snippet_message(event, text)


def announce_snippet_deleted(event: SnippetDeleted) -> None:
    """Announce that a snippet has been deleted."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    text = (
        f'{initiator_screen_name} hat das Snippet "{event.snippet_name}" '
        f'im Scope "{event.scope.type_}/{event.scope.name}" gelöscht.'
    )

    send_snippet_message(event, text)


# helpers


_SNIPPET_TYPE_LABELS = {
    SnippetType.document: 'Dokument',
    SnippetType.fragment: 'Fragment',
}


def _get_snippet_type_label(snippet_type: SnippetType) -> str:
    """Return label for snippet type."""
    return _SNIPPET_TYPE_LABELS.get(snippet_type, '?')


def send_snippet_message(event: _SnippetEvent, text: str) -> None:
    scope = 'snippet'
    scope_id = None

    send_message(event, scope, scope_id, text)
