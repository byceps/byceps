"""
byceps.services.seating.dbmodels.area
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ....database import db, generate_uuid
from ....typing import PartyID
from ....util.instances import ReprBuilder


class DbSeatingArea(db.Model):
    """A spatial representation of seats in one part of the party
    location.

    Seats can belong to different categories.
    """

    __tablename__ = 'seating_areas'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'slug'),
        db.UniqueConstraint('party_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True, nullable=False
    )
    slug = db.Column(db.UnicodeText, nullable=False)
    title = db.Column(db.UnicodeText, nullable=False)
    image_filename = db.Column(db.UnicodeText, nullable=True)
    image_width = db.Column(db.Integer, nullable=True)
    image_height = db.Column(db.Integer, nullable=True)

    def __init__(
        self,
        party_id: PartyID,
        slug: str,
        title: str,
        *,
        image_filename: Optional[str] = None,
        image_width: Optional[int] = None,
        image_height: Optional[int] = None,
    ) -> None:
        self.party_id = party_id
        self.slug = slug
        self.title = title
        self.image_filename = image_filename
        self.image_width = image_width
        self.image_height = image_height

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add('id', str(self.id))
            .add('party', self.party_id)
            .add_with_lookup('slug')
            .build()
        )
