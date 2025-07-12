"""
byceps.services.consent.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from byceps.services.user.models.user import UserID


ConsentSubjectID = NewType('ConsentSubjectID', UUID)


@dataclass(frozen=True, kw_only=True)
class ConsentSubject:
    id: ConsentSubjectID
    name: str
    title: str
    checkbox_label: str
    checkbox_link_target: str | None


@dataclass(frozen=True, kw_only=True)
class Consent:
    user_id: UserID
    subject_id: ConsentSubjectID
    expressed_at: datetime
