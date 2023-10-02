"""
byceps.services.party.dbmodels.setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.typing import PartyID
from byceps.util.instances import ReprBuilder


class DbPartySetting(db.Model):
    """A party-specific setting."""

    __tablename__ = 'party_settings'

    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), primary_key=True
    )
    name: Mapped[str] = mapped_column(db.UnicodeText, primary_key=True)
    value: Mapped[str] = mapped_column(db.UnicodeText)

    def __init__(self, party_id: PartyID, name: str, value: str) -> None:
        self.party_id = party_id
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('party_id')
            .add_with_lookup('name')
            .add_with_lookup('value')
            .build()
        )
