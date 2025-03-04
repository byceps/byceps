"""
byceps.services.snippet.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import _BaseEvent
from byceps.services.snippet.models import (
    SnippetID,
    SnippetScope,
    SnippetVersionID,
)


@dataclass(frozen=True)
class _SnippetEvent(_BaseEvent):
    snippet_id: SnippetID
    scope: SnippetScope
    snippet_name: str
    language_code: str


@dataclass(frozen=True)
class SnippetCreatedEvent(_SnippetEvent):
    snippet_version_id: SnippetVersionID


@dataclass(frozen=True)
class SnippetUpdatedEvent(_SnippetEvent):
    snippet_version_id: SnippetVersionID


@dataclass(frozen=True)
class SnippetDeletedEvent(_SnippetEvent):
    pass
