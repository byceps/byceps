"""
byceps.services.email.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from email.utils import formataddr
from typing import List

from ....typing import BrandID


@dataclass(frozen=True)
class Sender:
    address: str
    name: str

    def format(self):
        """Format the sender as a string value suitable for an e-mail header."""
        realname = self.name if self.name else False
        return formataddr((realname, self.address))


@dataclass(frozen=True)
class EmailConfig:
    id: str
    brand_id: BrandID
    sender: Sender
    contact_address: str


@dataclass(frozen=True)
class Message:
    sender: Sender
    recipients: List[str]
    subject: str
    body: str
