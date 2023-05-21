"""
byceps.events.snippet
~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.snippet.models import (
    SnippetID,
    SnippetScope,
    SnippetVersionID,
)

from .base import _BaseEvent


@dataclass(frozen=True)
class _SnippetEvent(_BaseEvent):
    snippet_id: SnippetID
    scope: SnippetScope
    snippet_name: str


@dataclass(frozen=True)
class SnippetCreatedEvent(_SnippetEvent):
    snippet_version_id: SnippetVersionID


@dataclass(frozen=True)
class SnippetUpdatedEvent(_SnippetEvent):
    snippet_version_id: SnippetVersionID


@dataclass(frozen=True)
class SnippetDeletedEvent(_SnippetEvent):
    pass
