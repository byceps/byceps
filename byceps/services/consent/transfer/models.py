"""
byceps.services.consent.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import NewType
from uuid import UUID

from attr import attrib, attrs

from ....typing import UserID


SubjectID = NewType('SubjectID', UUID)


@attrs(frozen=True, slots=True)
class Subject:
    id = attrib(type=SubjectID)
    name = attrib(type=str)
    title = attrib(type=str)
    type_ = attrib(type=str)


@attrs(frozen=True, slots=True)
class Consent:
    user_id = attrib(type=UserID)
    subject_id = attrib(type=SubjectID)
    expressed_at = attrib(type=datetime)
