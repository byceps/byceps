"""
byceps.services.site.models.site
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db
from ....typing import PartyID
from ....util.instances import ReprBuilder

from ..transfer.models import SiteID


class Site(db.Model):
    """A site."""
    __tablename__ = 'sites'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'title'),
    )

    id = db.Column(db.Unicode(40), primary_key=True)
    party_id = db.Column(db.Unicode(40), db.ForeignKey('parties.id'), index=True, nullable=False)
    title = db.Column(db.Unicode(20), nullable=False)

    def __init__(self, site_id: SiteID, party_id: PartyID, title: str) -> None:
        self.id = site_id
        self.party_id = party_id
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('party_id') \
            .build()
