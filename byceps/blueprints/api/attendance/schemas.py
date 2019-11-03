"""
byceps.blueprints.api.attendance.schemas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from marshmallow import fields, Schema


class CreateArchivedAttendanceRequest(Schema):
    user_id = fields.UUID()
    party_id = fields.Str()
