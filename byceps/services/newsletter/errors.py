"""
byceps.services.newsletter.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from .models import ListID


@dataclass(frozen=True)
class UnknownListIdError:
    list_id: ListID
