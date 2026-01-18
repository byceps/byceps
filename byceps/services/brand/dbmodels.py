"""
byceps.services.brand.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.brand.models import BrandID
from byceps.services.newsletter.models import ListID as NewsletterListID
from byceps.services.party.models import PartyID
from byceps.util.instances import ReprBuilder


class DbBrand(db.Model):
    """A party brand."""

    __tablename__ = 'brands'

    id: Mapped[BrandID] = mapped_column(db.UnicodeText, primary_key=True)
    title: Mapped[str] = mapped_column(db.UnicodeText, unique=True)
    image_filename: Mapped[str | None] = mapped_column(db.UnicodeText)
    archived: Mapped[bool] = mapped_column(default=False)

    def __init__(
        self,
        brand_id: BrandID,
        title: str,
        *,
        image_filename: str | None = None,
    ) -> None:
        self.id = brand_id
        self.title = title
        self.image_filename = image_filename

    def __repr__(self) -> str:
        return ReprBuilder(self).add_with_lookup('id').build()


class DbBrandCurrentParty(db.Model):
    __tablename__ = 'brand_current_parties'

    brand_id: Mapped[BrandID] = mapped_column(
        db.UnicodeText, db.ForeignKey('brands.id'), primary_key=True
    )
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('parties.id'),
        unique=True,
        nullable=False,
    )

    def __init__(self, brand_id: BrandID, party_id: PartyID) -> None:
        self.brand_id = brand_id
        self.party_id = party_id


class DbBrandNewsletterList(db.Model):
    __tablename__ = 'brand_newsletter_lists'

    brand_id: Mapped[BrandID] = mapped_column(
        db.UnicodeText, db.ForeignKey('brands.id'), primary_key=True
    )
    newsletter_list_id: Mapped[NewsletterListID] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('newsletter_lists.id'),
        unique=True,
        nullable=False,
    )

    def __init__(
        self, brand_id: BrandID, newsletter_list_id: NewsletterListID
    ) -> None:
        self.brand_id = brand_id
        self.newsletter_list_id = newsletter_list_id


class DbBrandSetting(db.Model):
    """A brand-specific setting."""

    __tablename__ = 'brand_settings'

    brand_id: Mapped[BrandID] = mapped_column(
        db.UnicodeText, db.ForeignKey('brands.id'), primary_key=True
    )
    name: Mapped[str] = mapped_column(db.UnicodeText, primary_key=True)
    value: Mapped[str] = mapped_column(db.UnicodeText)

    def __init__(self, brand_id: BrandID, name: str, value: str) -> None:
        self.brand_id = brand_id
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('brand_id')
            .add_with_lookup('name')
            .add_with_lookup('value')
            .build()
        )
