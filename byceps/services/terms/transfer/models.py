"""
byceps.services.terms.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
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
