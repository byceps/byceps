"""
byceps.services.snippet.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from .models import SnippetScope


@dataclass(frozen=True)
class _BaseSnippetError:
    scope: SnippetScope
    name: str
    language_code: str


@dataclass(frozen=True)
class SnippetAlreadyExistsError(_BaseSnippetError):
    pass


@dataclass(frozen=True)
class SnippetNotFoundError(_BaseSnippetError):
    pass


@dataclass(frozen=True)
class SnippetDeletionFailedError:
    pass
