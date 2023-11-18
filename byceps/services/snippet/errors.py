"""
byceps.services.snippet.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from .models import SnippetScope


@dataclass(frozen=True)
class SnippetNotFoundError:
    scope: SnippetScope
    name: str
    language_code: str
