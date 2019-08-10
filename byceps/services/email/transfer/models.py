"""
byceps.services.email.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List

from attr import attrs


@attrs(auto_attribs=True, frozen=True, slots=True)
class Message:
    sender: str
    recipients: List[str]
    subject: str
    body: str
