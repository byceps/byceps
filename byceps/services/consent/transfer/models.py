"""
byceps.services.consent.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from ....typing import UserID


SubjectID = NewType('SubjectID', UUID)


@dataclass(frozen=True)
class Subject:
    id: SubjectID
    name: str
    title: str
    type_: str


@dataclass(frozen=True)
class Consent:
    user_id: UserID
    subject_id: SubjectID
    expressed_at: datetime
