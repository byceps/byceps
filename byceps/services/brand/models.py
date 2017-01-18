# -*- coding: utf-8 -*-

"""
byceps.services.brand.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db
from ...util.instances import ReprBuilder


class Brand(db.Model):
    """A party brand."""
    __tablename__ = 'brands'

    id = db.Column(db.Unicode(20), primary_key=True)
    title = db.Column(db.Unicode(40), unique=True, nullable=False)

    def __init__(self, id, title):
        self.id = id
        self.title = title

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()
