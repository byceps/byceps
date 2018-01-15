"""
byceps.services.party.models.party
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple
from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from ....database import db
from ....typing import BrandID, PartyID
from ....util.datetime.range import DateTimeRange
from ....util.instances import ReprBuilder

from ...brand.models.brand import Brand


PartyTuple = namedtuple('PartyTuple', 'id, brand_id, title, starts_at, ends_at')


class Party(db.Model):
    """A party."""
    __tablename__ = 'parties'

    id = db.Column(db.Unicode(40), primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), index=True, nullable=False)
    brand = db.relationship(Brand, backref='parties')
    title = db.Column(db.Unicode(40), unique=True, nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, party_id: PartyID, brand_id: BrandID, title: str,
                 starts_at: datetime, ends_at: datetime) -> None:
        self.id = party_id
        self.brand_id = brand_id
        self.title = title
        self.starts_at = starts_at
        self.ends_at = ends_at

    @hybrid_property
    def range(self) -> DateTimeRange:
        return DateTimeRange(self.starts_at, self.ends_at)

    @property
    def is_over(self) -> bool:
        """Returns true if the party has ended."""
        return self.ends_at < datetime.now()

    def to_tuple(self) -> PartyTuple:
        """Return a tuple representation of (parts of) this entity."""
        return PartyTuple(
            self.id,
            self.brand_id,
            self.title,
            self.starts_at,
            self.ends_at,
        )

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()
