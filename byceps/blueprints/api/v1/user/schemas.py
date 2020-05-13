"""
byceps.blueprints.api.v1.user.schemas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from marshmallow import fields, Schema


class InvalidateEmailAddressRequest(Schema):
    email_address = fields.Str(required=True)
    reason = fields.Str(required=True)
