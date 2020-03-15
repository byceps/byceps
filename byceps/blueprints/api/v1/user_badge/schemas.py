"""
byceps.blueprints.api.v1.user_badge.schemas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from marshmallow import fields, Schema


class AwardBadgeToUserRequest(Schema):
    badge_slug = fields.Str()
    user_id = fields.UUID()
    initiator_id = fields.UUID()
