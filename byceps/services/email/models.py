"""
byceps.services.email.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...database import db
from ...typing import BrandID
from ...util.instances import ReprBuilder


class EmailConfig(db.Model):
    """An e-mail configuration."""

    __tablename__ = 'email_configs'

    id = db.Column(db.UnicodeText, primary_key=True)
    brand_id = db.Column(db.UnicodeText, db.ForeignKey('brands.id'), index=True, unique=True, nullable=False)
    sender_address = db.Column(db.UnicodeText, nullable=False)
    sender_name = db.Column(db.UnicodeText, nullable=True)
    contact_address = db.Column(db.UnicodeText, nullable=True)

    def __init__(
        self,
        config_id: str,
        brand_id: BrandID,
        sender_address: str,
        *,
        sender_name: Optional[str] = None,
        contact_address: Optional[str] = None,
    ) -> None:
        self.id = config_id
        self.brand_id = brand_id
        self.sender_address = sender_address
        self.sender_name = sender_name
        self.contact_address = contact_address

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()
