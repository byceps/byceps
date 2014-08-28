# -*- coding: utf-8 -*-

"""
byceps.blueprints.terms.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from datetime import datetime
from operator import attrgetter

from flask import g

from ...database import BaseQuery, db, generate_uuid
from ...util.instances import ReprBuilder

from ..brand.models import Brand
from ..user.models import User


class TermsVersionQuery(BaseQuery):

    def for_current_brand(self):
        return self.filter_by(brand=g.party.brand)

    def latest_first(self):
        return self.order_by(TermsVersion.created_at.desc())

    def get_current(self):
        return self.for_current_brand().latest_first().first()


class TermsVersion(db.Model):
    """A specific version of a specific brand's terms and conditions."""
    __tablename__ = 'terms_versions'
    query_class = TermsVersionQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'))
    brand = db.relationship(Brand)
    created_at = db.Column(db.DateTime, default=datetime.now)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    creator = db.relationship(User)
    body = db.Column(db.UnicodeText)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('brand', self.brand_id) \
            .add_with_lookup('created_at') \
            .build()
