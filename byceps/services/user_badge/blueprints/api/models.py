"""
byceps.services.user_badge.blueprints.api.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, kw_only=True)
class AwardBadgeToUserRequest:
    badge_slug: str
    awardee_id: UUID
    initiator_id: UUID
