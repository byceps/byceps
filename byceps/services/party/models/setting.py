"""
byceps.services.party.models.setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple

from ....database import db
from ....typing import PartyID
from ....util.instances import ReprBuilder


SettingTuple = namedtuple('PartySettingTuple', 'party_id, name, value')


class Setting(db.Model):
    """A party-specific setting."""
    __tablename__ = 'party_settings'

    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), primary_key=True)
    name = db.Column(db.Unicode(40), primary_key=True)
    value = db.Column(db.Unicode(200))

    def __init__(self, party_id: PartyID, name: str, value: str) -> None:
        self.party_id = party_id
        self.name = name
        self.value = value

    def to_tuple(self) -> SettingTuple:
        """Return a tuple representation of this entity."""
        return SettingTuple(
            self.party_id,
            self.name,
            self.value,
        )

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('party_id') \
            .add_with_lookup('name') \
            .add_with_lookup('value') \
            .build()
