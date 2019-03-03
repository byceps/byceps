"""
byceps.services.snippet.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum
from typing import NewType
from uuid import UUID

from attr import attrib, attrs

from ....typing import PartyID


@attrs(frozen=True, slots=True)
class Scope:
    type_ = attrib(type=str)
    name = attrib(type=str)

    @classmethod
    def for_party(cls, party_id: PartyID):
        return cls('party', str(party_id))


SnippetID = NewType('SnippetID', UUID)


SnippetType = Enum('SnippetType', ['document', 'fragment'])


SnippetVersionID = NewType('SnippetVersionID', UUID)


MountpointID = NewType('MountpointID', UUID)
