"""
byceps.services.consent.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType, Optional
from uuid import UUID

from byceps.typing import UserID


ConsentSubjectID = NewType('ConsentSubjectID', UUID)


@dataclass(frozen=True)
class ConsentSubject:
    id: ConsentSubjectID
    name: str
    title: str
    checkbox_label: str
    checkbox_link_target: Optional[str]


@dataclass(frozen=True)
class Consent:
    user_id: UserID
    subject_id: ConsentSubjectID
    expressed_at: datetime
