"""
byceps.services.email.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db
from ...typing import BrandID
from ...util.instances import ReprBuilder


class EmailConfig(db.Model):
    """E-mail configuration for a brand."""
    __tablename__ = 'email_configs'

    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), primary_key=True)
    sender_address = db.Column(db.Unicode(80), nullable=False)

    def __init__(self, brand_id: BrandID, sender_address: str) -> None:
        self.brand_id = brand_id
        self.sender_address = sender_address

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('brand') \
            .build()
