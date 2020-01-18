"""
byceps.events.snippet
~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass

from ..services.snippet.transfer.models import SnippetVersionID

from .base import _BaseEvent


@dataclass(frozen=True)
class _SnippetEvent(_BaseEvent):
    snippet_version_id: SnippetVersionID


@dataclass(frozen=True)
class SnippetCreated(_SnippetEvent):
    pass


@dataclass(frozen=True)
class SnippetUpdated(_SnippetEvent):
    pass
