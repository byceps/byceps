"""
byceps.blueprints.api.v1.user_badge.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from pydantic import BaseModel


class AwardBadgeToUserRequest(BaseModel):
    badge_slug: str
    user_id: UUID
    initiator_id: UUID
