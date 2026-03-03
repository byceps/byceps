"""
byceps.services.user_badge.blueprints.api.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from pydantic import BaseModel


class AwardBadgeToUserRequest(BaseModel):
    badge_slug: str
    awardee_id: UUID
    initiator_id: UUID
