"""
byceps.services.seating.models.area
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import BaseQuery, db, generate_uuid
from ....typing import PartyID
from ....util.instances import ReprBuilder


class AreaQuery(BaseQuery):

    def for_party(self, party_id: PartyID) -> BaseQuery:
        return self.filter_by(party_id=party_id)


class Area(db.Model):
    """A spatial representation of seats in one part of the party
    location.

    Seats can belong to different categories.
    """

    __tablename__ = 'seating_areas'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'slug'),
        db.UniqueConstraint('party_id', 'title'),
    )
    query_class = AreaQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.UnicodeText, db.ForeignKey('parties.id'), index=True, nullable=False)
    slug = db.Column(db.UnicodeText, nullable=False)
    title = db.Column(db.UnicodeText, nullable=False)
    image_filename = db.Column(db.UnicodeText, nullable=True)
    image_width = db.Column(db.Integer, nullable=True)
    image_height = db.Column(db.Integer, nullable=True)

    def __init__(self, party_id: PartyID, slug: str, title: str) -> None:
        self.party_id = party_id
        self.slug = slug
        self.title = title

    def set_image(self, filename: str, width: int, height: int) -> None:
        self.image_filename = filename
        self.image_width = width
        self.image_height = height

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add('id', str(self.id)) \
            .add('party', self.party_id) \
            .add_with_lookup('slug') \
            .build()
