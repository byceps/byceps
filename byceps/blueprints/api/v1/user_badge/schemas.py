"""
byceps.blueprints.api.v1.user_badge.schemas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from marshmallow import fields, Schema


class AwardBadgeToUserRequest(Schema):
    badge_slug = fields.Str(required=True)
    user_id = fields.UUID(required=True)
    initiator_id = fields.UUID(required=True)
