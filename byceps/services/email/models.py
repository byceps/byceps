"""
byceps.services.email.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from email.utils import formataddr
from typing import Optional

from byceps.typing import BrandID


@dataclass(frozen=True)
class NameAndAddress:
    name: Optional[str]
    address: str

    def format(self):
        """Format the name and address as a string value suitable for an
        e-mail header.
        """
        return formataddr((self.name, self.address))


@dataclass(frozen=True)
class EmailConfig:
    brand_id: BrandID
    sender: NameAndAddress
    contact_address: str


@dataclass(frozen=True)
class Message:
    sender: NameAndAddress
    recipients: list[str]
    subject: str
    body: str
