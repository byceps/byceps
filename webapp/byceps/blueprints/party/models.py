# -*- coding: utf-8 -*-

"""
byceps.blueprints.party.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from datetime import datetime

from ...database import db
from ...util.instances import ReprBuilder

from ..brand.models import Brand


class Party(db.Model):
    """A party."""
    __tablename__ = 'parties'

    id = db.Column(db.Unicode(40), primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'))
    brand = db.relationship(Brand, backref='parties')
    title = db.Column(db.Unicode(40), unique=True)
    starts_at = db.Column(db.DateTime)
    ends_at = db.Column(db.DateTime)
    is_archived = db.Column(db.Boolean, default=False)

    @property
    def is_over(self):
        """Returns true if the party has ended."""
        return self.ends_at < datetime.now()

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('brand', self.brand.title) \
            .add_with_lookup('title') \
            .add_with_lookup('starts_at') \
            .add_with_lookup('ends_at') \
            .add_with_lookup('is_archived') \
            .build()
