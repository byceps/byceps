"""
byceps.services.terms.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType
from uuid import UUID

from attr import attrs


DocumentID = NewType('DocumentID', str)


VersionID = NewType('VersionID', UUID)


@attrs(auto_attribs=True, frozen=True, slots=True)
class Document:
    id: DocumentID
    title: str
    current_version_id: VersionID
