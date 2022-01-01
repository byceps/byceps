"""
byceps.blueprints.api.v1.attendance.schemas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from marshmallow import fields, Schema


class CreateArchivedAttendanceRequest(Schema):
    user_id = fields.UUID(required=True)
    party_id = fields.Str(required=True)
