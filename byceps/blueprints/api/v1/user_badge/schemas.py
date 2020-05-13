"""
byceps.blueprints.api.v1.user_badge.schemas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from marshmallow import fields, Schema


class AwardBadgeToUserRequest(Schema):
    badge_slug = fields.Str(required=True)
    user_id = fields.UUID(required=True)
    initiator_id = fields.UUID(required=True)
