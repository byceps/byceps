# -*- coding: utf-8 -*-

"""
byceps.services.orga.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...blueprints.user.models.user import User
from ...database import db
from ...util.instances import ReprBuilder

from ..brand.models import Brand


class OrgaFlag(db.Model):
    """A user's organizer status for a single brand."""
    __tablename__ = 'orga_flags'

    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), primary_key=True)
    brand = db.relationship(Brand)
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User)

    def __init__(self, brand_id, user_id):
        self.brand_id = brand_id
        self.user_id = user_id

    def __repr__(self):
        return ReprBuilder(self) \
            .add('brand', self.brand_id) \
            .add('user', self.user.screen_name) \
            .build()
