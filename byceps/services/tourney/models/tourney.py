"""
byceps.services.tourney.models.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db, generate_uuid

from ....util.instances import ReprBuilder

from .tourney_category import TourneyCategory


class Tourney(db.Model):
    """A tournament."""

    __tablename__ = 'tourneys'
    __table_args__ = (
        db.UniqueConstraint('category_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    category_id = db.Column(db.Uuid, db.ForeignKey('tourney_categories.id'), index=True, nullable=False)
    category = db.relationship(TourneyCategory)
    title = db.Column(db.UnicodeText, nullable=False)

    def __init__(self, category: TourneyCategory, title: str) -> None:
        self.category = category
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('category') \
            .add_with_lookup('title') \
            .build()
