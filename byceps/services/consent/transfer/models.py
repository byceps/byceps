"""
byceps.services.consent.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import NewType
from uuid import UUID

from attr import attrs

from ....typing import UserID


SubjectID = NewType('SubjectID', UUID)


@attrs(auto_attribs=True, frozen=True, slots=True)
class Subject:
    id: SubjectID
    name: str
    title: str
    type_: str


@attrs(auto_attribs=True, frozen=True, slots=True)
class Consent:
    user_id: UserID
    subject_id: SubjectID
    expressed_at: datetime
