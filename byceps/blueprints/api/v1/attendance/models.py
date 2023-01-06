"""
byceps.blueprints.api.v1.attendance.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from pydantic import BaseModel


class CreateArchivedAttendanceRequest(BaseModel):
    user_id: UUID
    party_id: str
