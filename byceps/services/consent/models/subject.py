"""
byceps.services.consent.models.subject
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db, generate_uuid
from ....typing import BrandID
from ....util.instances import ReprBuilder

from ...brand.models.brand import Brand


class Subject(db.Model):
    """A subject that requires users' consent."""
    __tablename__ = 'consent_subjects'
    __table_args__ = (
        db.UniqueConstraint('brand_id', 'name'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), nullable=False)
    brand = db.relationship(Brand)
    name = db.Column(db.Unicode(40), nullable=False)

    def __init__(brand_id: BrandID, name: str) -> None:
        self.brand_id = brand_id
        self.name = name

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('brand', self.brand_id) \
            .add_with_lookup('name') \
            .build()
