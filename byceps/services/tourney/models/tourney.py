"""
byceps.services.tourney.models.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType
from uuid import UUID

from ....database import db, generate_uuid

from ....util.instances import ReprBuilder

from .tourney_category import TourneyCategory


TourneyID = NewType('TourneyID', UUID)


class Tourney(db.Model):
    """A tournament."""

    __tablename__ = 'tourneys'
    __table_args__ = (
        db.UniqueConstraint('group_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    group_id = db.Column(db.Uuid, db.ForeignKey('tourney_groups.id'), index=True, nullable=False)
    group = db.relationship(TourneyCategory)
    title = db.Column(db.UnicodeText, nullable=False)

    def __init__(self, group: TourneyCategory, title: str) -> None:
        self.group = group
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('group') \
            .add_with_lookup('title') \
            .build()
