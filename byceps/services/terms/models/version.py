"""
byceps.services.terms.models.version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import NewType
from uuid import UUID

from ....database import BaseQuery, db, generate_uuid
from ....typing import BrandID, UserID
from ....util.instances import ReprBuilder

from ...brand.models.brand import Brand
from ...user.models.user import User


VersionID = NewType('VersionID', UUID)


class VersionQuery(BaseQuery):

    def for_brand_id(self, brand_id: BrandID) -> BaseQuery:
        return self.filter_by(brand_id=brand_id)

    def latest_first(self) -> BaseQuery:
        return self.order_by(Version.created_at.desc())


class Version(db.Model):
    """A specific version of a specific brand's terms and conditions."""
    __tablename__ = 'terms_versions'
    __table_args__ = (
        db.UniqueConstraint('brand_id', 'title'),
    )
    query_class = VersionQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), nullable=False)
    brand = db.relationship(Brand)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship(User)
    title = db.Column(db.Unicode(40), nullable=False)
    body = db.Column(db.UnicodeText, nullable=False)

    def __init__(self, brand_id: BrandID, creator_id: UserID, title: str,
                 body: str) -> None:
        self.brand_id = brand_id
        self.creator_id = creator_id
        self.title = title
        self.body = body

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('brand', self.brand_id) \
            .add_with_lookup('created_at') \
            .add_with_lookup('title') \
            .build()


class CurrentVersionAssociation(db.Model):
    __tablename__ = 'terms_current_versions'

    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), primary_key=True)
    version_id = db.Column(db.Uuid, db.ForeignKey('terms_versions.id'), unique=True, nullable=False)
    version = db.relationship(Version)

    def __init__(self, brand_id: BrandID, version_id: VersionID) -> None:
        self.brand_id = brand_id
        self.version_id = version_id
