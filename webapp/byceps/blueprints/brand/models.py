# -*- coding: utf-8 -*-

"""
byceps.blueprints.brand.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...database import db


class Brand(db.Model):
    """A party brand."""
    __tablename__ = 'brands'

    id = db.Column(db.Unicode(20), primary_key=True)
    title = db.Column(db.Unicode(40), unique=True)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('title') \
            .add_custom('{:d} parties'.format(len(self.parties))) \
            .build()
