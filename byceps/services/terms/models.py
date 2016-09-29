# -*- coding: utf-8 -*-

"""
byceps.services.terms.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy.ext.hybrid import hybrid_property

from ...blueprints.brand.models import Brand
from ...blueprints.user.models.user import User
from ...database import BaseQuery, db, generate_uuid
from ...util.instances import ReprBuilder


class VersionQuery(BaseQuery):

    def for_brand_id(self, brand_id):
        return self.filter_by(brand_id=brand_id)

    def latest_first(self):
        return self.order_by(Version.created_at.desc())


class Version(db.Model):
    """A specific version of a specific brand's terms and conditions."""
    __tablename__ = 'terms_versions'
    __table_args__ = (
        db.UniqueConstraint('brand_id', 'title'),
    )
    query_class = VersionQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'))
    brand = db.relationship(Brand)
    created_at = db.Column(db.DateTime, default=datetime.now)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    creator = db.relationship(User)
    title = db.Column(db.Unicode(40), nullable=False)
    body = db.Column(db.UnicodeText)

    def __init__(self, brand_id, creator_id, body):
        self.brand_id = brand_id
        self.creator_id = creator_id
        self.body = body

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('brand', self.brand_id) \
            .add_with_lookup('created_at') \
            .build()


ConsentContext = Enum('ConsentContext', ['account_creation', 'separate_action'])


class Consent(db.Model):
    """A user's consent to a specific version of a brand's terms and
    conditions.
    """
    __tablename__ = 'terms_consents'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User)
    version_id = db.Column(db.Uuid, db.ForeignKey('terms_versions.id'), primary_key=True)
    version = db.relationship(Version)
    expressed_at = db.Column(db.DateTime, default=datetime.now, primary_key=True)
    _context = db.Column('context', db.Unicode(20), primary_key=True)

    def __init__(self, user_id, version_id, context):
        self.user_id = user_id
        self.version_id = version_id
        self.context = context

    @hybrid_property
    def context(self):
        return ConsentContext[self._context]

    @context.setter
    def context(self, context):
        assert context is not None
        self._context = context.name
