"""
byceps.services.tourney.dbmodels.participant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from ...user.dbmodels.user import User

from ..transfer.models import TourneyID

from .tourney import Tourney


class Participant(db.Model):
    """One or more players participating in a tourney as a single unit."""

    __tablename__ = 'tourney_participants'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    tourney_id = db.Column(db.Uuid, db.ForeignKey('tourneys.id'), index=True, nullable=False)
    tourney = db.relationship(Tourney)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    created_by = db.relationship(User)
    title = db.Column(db.UnicodeText, nullable=False)
    max_size = db.Column(db.Integer, nullable=True)

    def __init__(
        self, tourney_id: TourneyID, title: str, max_size: int
    ) -> None:
        self.tourney_id = tourney_id
        self.title = title
        self.max_size = max_size

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('tourney') \
            .add_with_lookup('title') \
            .add_with_lookup('max_size') \
            .build()
