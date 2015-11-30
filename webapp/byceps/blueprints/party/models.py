# -*- coding: utf-8 -*-

"""
byceps.blueprints.party.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from ...database import BaseQuery, db
from ...util.datetime import DateTimeRange
from ...util.instances import ReprBuilder

from ..brand.models import Brand


class PartyQuery(BaseQuery):

    def for_brand(self, brand):
        return self.filter_by(brand_id=brand.id)


class Party(db.Model):
    """A party."""
    __tablename__ = 'parties'
    __table_args__ = (
        db.UniqueConstraint('brand_id', 'number'),
    )
    query_class = PartyQuery

    id = db.Column(db.Unicode(40), primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), index=True, nullable=False)
    brand = db.relationship(Brand, backref='parties')
    number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Unicode(40), unique=True, nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, id, brand, number, title, starts_at, ends_at):
        self.id = id
        self.brand = brand
        self.number = number
        self.title = title
        self.starts_at = starts_at
        self.ends_at = ends_at

    @hybrid_property
    def range(self):
        return DateTimeRange(self.starts_at, self.ends_at)

    @property
    def is_over(self):
        """Returns true if the party has ended."""
        return self.ends_at < datetime.now()

    @property
    def number_prefix(self):
        return '{}-{:02d}'.format(self.brand.code, self.number)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()
