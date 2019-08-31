"""
byceps.services.email.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from email.utils import formataddr
from typing import List

from attr import attrs


@attrs(auto_attribs=True, frozen=True, slots=True)
class Sender:
    address: str
    name: str

    def format(self):
        """Format the sender as a string value suitable for an e-mail header."""
        realname = self.name if self.name else False
        return formataddr((realname, self.address))


@attrs(auto_attribs=True, frozen=True, slots=True)
class Message:
    sender: Sender
    recipients: List[str]
    subject: str
    body: str
