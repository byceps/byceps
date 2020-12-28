"""
byceps.announce.common.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce snippet events.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.snippet import SnippetCreated, SnippetDeleted, SnippetUpdated
from ...services.snippet.transfer.models import SnippetType

from ..helpers import get_screen_name_or_fallback


def assemble_text_for_snippet_created(event: SnippetCreated) -> str:
    editor_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    type_label = _get_snippet_type_label(event.snippet_type)

    return (
        f'{editor_screen_name} hat das Snippet-{type_label} '
        f'"{event.snippet_name}" im Scope '
        f'"{event.scope.type_}/{event.scope.name}" angelegt.'
    )


def assemble_text_for_snippet_updated(event: SnippetUpdated) -> str:
    editor_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )
    type_label = _get_snippet_type_label(event.snippet_type)

    return (
        f'{editor_screen_name} hat das Snippet-{type_label} '
        f'"{event.snippet_name}" im Scope '
        f'"{event.scope.type_}/{event.scope.name}" aktualisiert.'
    )


def assemble_text_for_snippet_deleted(event: SnippetDeleted) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    return (
        f'{initiator_screen_name} hat das Snippet "{event.snippet_name}" '
        f'im Scope "{event.scope.type_}/{event.scope.name}" gelöscht.'
    )


# helpers


_SNIPPET_TYPE_LABELS = {
    SnippetType.document: 'Dokument',
    SnippetType.fragment: 'Fragment',
}


def _get_snippet_type_label(snippet_type: SnippetType) -> str:
    """Return label for snippet type."""
    return _SNIPPET_TYPE_LABELS.get(snippet_type, '?')
