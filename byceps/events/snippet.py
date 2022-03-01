"""
byceps.events.snippet
~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from ..services.snippet.transfer.models import (
    Scope,
    SnippetID,
    SnippetType,
    SnippetVersionID,
)

from .base import _BaseEvent


@dataclass(frozen=True)
class _SnippetEvent(_BaseEvent):
    snippet_id: SnippetID
    scope: Scope
    snippet_name: str
    snippet_type: SnippetType


@dataclass(frozen=True)
class SnippetCreated(_SnippetEvent):
    snippet_version_id: SnippetVersionID


@dataclass(frozen=True)
class SnippetUpdated(_SnippetEvent):
    snippet_version_id: SnippetVersionID


@dataclass(frozen=True)
class SnippetDeleted(_SnippetEvent):
    pass
