"""
byceps.blueprints.api.v1.user.schemas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from marshmallow import fields, Schema


class InvalidateEmailAddressRequest(Schema):
    email_address = fields.Str(required=True)
    reason = fields.Str(required=True)
