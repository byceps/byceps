"""
byceps.services.email.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...database import db
from ...typing import BrandID
from ...util.instances import ReprBuilder


class EmailConfig(db.Model):
    """E-mail configuration for a brand."""
    __tablename__ = 'email_configs'

    brand_id = db.Column(db.UnicodeText, db.ForeignKey('brands.id'), primary_key=True)
    sender_address = db.Column(db.UnicodeText, nullable=False)
    sender_name = db.Column(db.UnicodeText, nullable=True)

    def __init__(self, brand_id: BrandID, sender_address: str,
                 *, sender_name: Optional[str]=None) -> None:
        self.brand_id = brand_id
        self.sender_address = sender_address
        self.sender_name = sender_name

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('brand') \
            .build()
