"""
byceps.announce.irc.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce snippet events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...events.snippet import SnippetCreated, SnippetDeleted, SnippetUpdated
from ...services.snippet.transfer.models import SnippetType
from ...services.user import service as user_service
from ...signals import snippet as snippet_signals
from ...typing import UserID
from ...util.irc import send_message
from ...util.jobqueue import enqueue

from ..helpers import get_screen_name_or_fallback

from ._config import CHANNEL_ORGA_LOG


@snippet_signals.snippet_created.connect
def _on_snippet_created(sender, *, event: SnippetCreated = None) -> None:
    enqueue(announce_snippet_created, event)


def announce_snippet_created(event: SnippetCreated) -> None:
    """Announce that a snippet has been created."""
    channels = [CHANNEL_ORGA_LOG]

    editor_screen_name = _get_screen_name(event.initiator_id)
    type_label = _get_snippet_type_label(event.snippet_type)

    text = (
        f'{editor_screen_name} hat das Snippet-{type_label} '
        f'"{event.snippet_name}" im Scope '
        f'"{event.scope.type_}/{event.scope.name}" angelegt.'
    )

    send_message(channels, text)


@snippet_signals.snippet_updated.connect
def _on_snippet_updated(sender, *, event: SnippetUpdated = None) -> None:
    enqueue(announce_snippet_updated, event)


def announce_snippet_updated(event: SnippetUpdated) -> None:
    """Announce that a snippet has been updated."""
    channels = [CHANNEL_ORGA_LOG]

    editor_screen_name = _get_screen_name(event.initiator_id)
    type_label = _get_snippet_type_label(event.snippet_type)

    text = (
        f'{editor_screen_name} hat das Snippet-{type_label} '
        f'"{event.snippet_name}" im Scope '
        f'"{event.scope.type_}/{event.scope.name}" aktualisiert.'
    )

    send_message(channels, text)


@snippet_signals.snippet_deleted.connect
def _on_snippet_deleted(sender, *, event: SnippetDeleted = None) -> None:
    enqueue(announce_snippet_deleted, event)


def announce_snippet_deleted(event: SnippetDeleted) -> None:
    """Announce that a snippet has been deleted."""
    channels = [CHANNEL_ORGA_LOG]

    initiator_screen_name = _get_screen_name(event.initiator_id)

    text = (
        f'{initiator_screen_name} hat das Snippet "{event.snippet_name}" '
        f'im Scope "{event.scope.type_}/{event.scope.name}" gelöscht.'
    )

    send_message(channels, text)


_SNIPPET_TYPE_LABELS = {
    SnippetType.document: 'Dokument',
    SnippetType.fragment: 'Fragment',
}


def _get_snippet_type_label(snippet_type: SnippetType) -> str:
    """Return label for snippet type."""
    return _SNIPPET_TYPE_LABELS.get(snippet_type, '?')


def _get_screen_name(user_id: UserID) -> str:
    screen_name = user_service.find_screen_name(user_id)
    return get_screen_name_or_fallback(screen_name)
