"""
byceps.services.user_badge.dbmodels.awarding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from ....database import db, generate_uuid
from ....typing import UserID

from ..transfer.models import BadgeID


class DbBadgeAwarding(db.Model):
    """The awarding of a badge to a user."""

    __tablename__ = 'user_badge_awardings'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    badge_id = db.Column(
        db.Uuid, db.ForeignKey('user_badges.id'), nullable=False
    )
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    awarded_at = db.Column(db.DateTime, nullable=False)

    def __init__(
        self, badge_id: BadgeID, user_id: UserID, awarded_at: datetime
    ) -> None:
        self.badge_id = badge_id
        self.user_id = user_id
        self.awarded_at = awarded_at
