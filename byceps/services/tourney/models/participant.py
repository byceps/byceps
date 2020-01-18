"""
byceps.services.tourney.models.participant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from ...user.models.user import User

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

    def __init__(self, tourney: Tourney, title: str, max_size: int) -> None:
        self.tourney = tourney
        self.title = title
        self.max_size = max_size

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('tourney') \
            .add_with_lookup('title') \
            .add_with_lookup('max_size') \
            .build()
