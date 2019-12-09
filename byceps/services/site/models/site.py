"""
byceps.services.site.models.site
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ....database import db
from ....typing import PartyID
from ....util.instances import ReprBuilder

from ..transfer.models import SiteID


class Site(db.Model):
    """A site."""

    __tablename__ = 'sites'

    id = db.Column(db.UnicodeText, primary_key=True)
    title = db.Column(db.UnicodeText, unique=True, nullable=False)
    server_name = db.Column(db.UnicodeText, unique=True, nullable=False)
    email_config_id = db.Column(db.UnicodeText, db.ForeignKey('email_configs.id'), nullable=False)
    party_id = db.Column(db.UnicodeText, db.ForeignKey('parties.id'), index=True, nullable=True)
    enabled = db.Column(db.Boolean, nullable=False)
    user_account_creation_enabled = db.Column(db.Boolean, nullable=False)
    login_enabled = db.Column(db.Boolean, nullable=False)

    def __init__(
        self,
        site_id: SiteID,
        title: str,
        server_name: str,
        email_config_id: str,
        enabled: bool,
        user_account_creation_enabled: bool,
        login_enabled: bool,
        *,
        party_id: Optional[PartyID] = None,
    ) -> None:
        self.id = site_id
        self.title = title
        self.server_name = server_name
        self.email_config_id = email_config_id
        self.party_id = party_id
        self.enabled = enabled
        self.user_account_creation_enabled = user_account_creation_enabled
        self.login_enabled = login_enabled

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('party_id') \
            .build()
