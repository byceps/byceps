# -*- coding: utf-8 -*-

"""
byceps.blueprints.seating.models.area
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import BaseQuery, db, generate_uuid
from ....util.instances import ReprBuilder

from ...party.models import Party


class AreaQuery(BaseQuery):

    def for_party(self, party):
        return self.filter_by(party_id=party.id)


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
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), index=True, nullable=False)
    party = db.relationship(Party, backref='seating_areas')
    slug = db.Column(db.Unicode(40), nullable=False)
    title = db.Column(db.Unicode(40), nullable=False)
    image_filename = db.Column(db.Unicode(40), nullable=True)
    image_width = db.Column(db.Integer, nullable=True)
    image_height = db.Column(db.Integer, nullable=True)

    def __init__(self, party, slug, title):
        self.party = party
        self.slug = slug
        self.title = title

    def set_image(self, filename, width, height):
        self.image_filename = filename
        self.image_width = width
        self.image_height = height

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('party') \
            .add_with_lookup('slug') \
            .build()
