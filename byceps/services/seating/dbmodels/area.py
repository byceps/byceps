"""
byceps.services.seating.dbmodels.area
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.seating.models import SeatingAreaID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid4


class DbSeatingArea(db.Model):
    """A spatial representation of seats in one part of the party
    location.

    Seats can belong to different categories.
    """

    __tablename__ = 'seating_areas'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'slug'),
        db.UniqueConstraint('party_id', 'title'),
    )

    id: Mapped[SeatingAreaID] = mapped_column(db.Uuid, primary_key=True)
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True
    )
    slug: Mapped[str] = mapped_column(db.UnicodeText)
    title: Mapped[str] = mapped_column(db.UnicodeText)
    image_filename: Mapped[str | None] = mapped_column(db.UnicodeText)
    image_width: Mapped[int | None]
    image_height: Mapped[int | None]

    def __init__(
        self,
        area_id: SeatingAreaID,
        party_id: PartyID,
        slug: str,
        title: str,
        *,
        image_filename: str | None = None,
        image_width: int | None = None,
        image_height: int | None = None,
    ) -> None:
        self.id = area_id
        self.party_id = party_id
        self.slug = slug
        self.title = title
        self.image_filename = image_filename
        self.image_width = image_width
        self.image_height = image_height

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add('id', str(self.id))
            .add('party', self.party_id)
            .add_with_lookup('slug')
            .build()
        )
