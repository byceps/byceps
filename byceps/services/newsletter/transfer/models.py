"""
byceps.services.newsletter.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import NewType


ListID = NewType('ListID', str)


@dataclass(frozen=True)
class List:
    id: ListID
    title: str
