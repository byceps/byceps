"""
byceps.services.email.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.typing import BrandID
from byceps.util.instances import ReprBuilder


class DbEmailConfig(db.Model):
    """An e-mail configuration."""

    __tablename__ = 'email_configs'

    brand_id: Mapped[BrandID] = mapped_column(
        db.UnicodeText, db.ForeignKey('brands.id'), primary_key=True
    )
    sender_address: Mapped[str] = mapped_column(db.UnicodeText)
    sender_name: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        db.UnicodeText
    )
    contact_address: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        db.UnicodeText
    )

    def __init__(
        self,
        brand_id: BrandID,
        sender_address: str,
        *,
        sender_name: str | None = None,
        contact_address: str | None = None,
    ) -> None:
        self.brand_id = brand_id
        self.sender_address = sender_address
        self.sender_name = sender_name
        self.contact_address = contact_address

    def __repr__(self) -> str:
        return ReprBuilder(self).add_with_lookup('brand_id').build()
