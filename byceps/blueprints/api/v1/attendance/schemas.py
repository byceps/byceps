"""
byceps.blueprints.api.v1.attendance.schemas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from marshmallow import fields, Schema


class CreateArchivedAttendanceRequest(Schema):
    user_id = fields.UUID()
    party_id = fields.Str()
