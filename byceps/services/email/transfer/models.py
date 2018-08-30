"""
byceps.services.email.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from attr import attrib, attrs


@attrs(frozen=True, slots=True)
class Message:
    sender = attrib(type=str)
    recipients = attrib()
    subject = attrib(type=str)
    body = attrib(type=str)
