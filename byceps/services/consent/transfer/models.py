"""
byceps.services.consent.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType
from uuid import UUID

from attr import attrib, attrs


SubjectID = NewType('SubjectID', UUID)


@attrs(frozen=True, slots=True)
class Subject:
    id = attrib(type=SubjectID)
    name = attrib(type=str)
    title = attrib(type=str)
