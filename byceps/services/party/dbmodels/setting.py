"""
byceps.services.party.dbmodels.setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ....database import db
from ....typing import PartyID
from ....util.instances import ReprBuilder


class DbSetting(db.Model):
    """A party-specific setting."""

    __tablename__ = 'party_settings'

    party_id = db.Column(
        db.UnicodeText, db.ForeignKey('parties.id'), primary_key=True
    )
    name = db.Column(db.UnicodeText, primary_key=True)
    value = db.Column(db.UnicodeText)

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
