"""
byceps.services.consent.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType, Optional
from uuid import UUID

from ....typing import UserID


SubjectID = NewType('SubjectID', UUID)


@dataclass(frozen=True)
class Subject:
    id: SubjectID
    name: str
    title: str
    checkbox_label: str
    checkbox_link_target: Optional[str]


@dataclass(frozen=True)
class Consent:
    user_id: UserID
    subject_id: SubjectID
    expressed_at: datetime
