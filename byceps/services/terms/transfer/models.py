"""
byceps.services.terms.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import NewType
from uuid import UUID


DocumentID = NewType('DocumentID', str)


VersionID = NewType('VersionID', UUID)


@dataclass(frozen=True)
class Document:
    id: DocumentID
    title: str
    current_version_id: VersionID
