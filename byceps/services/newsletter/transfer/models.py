"""
byceps.services.newsletter.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType


ListID = NewType('ListID', str)


@dataclass(frozen=True)
class List:
    id: ListID
    title: str


@dataclass(frozen=True)
class Subscriber:
    screen_name: str
    email_address: str
