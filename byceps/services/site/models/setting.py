"""
byceps.services.site.models.setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ....database import db
from ....util.instances import ReprBuilder

from ..transfer.models import SiteID


class Setting(db.Model):
    """A site-specific setting."""

    __tablename__ = 'site_settings'

    site_id = db.Column(db.UnicodeText, db.ForeignKey('sites.id'), primary_key=True, index=True)
    name = db.Column(db.UnicodeText, primary_key=True)
    value = db.Column(db.UnicodeText)

    def __init__(self, site_id: SiteID, name: str, value: str) -> None:
        self.site_id = site_id
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('site_id') \
            .add_with_lookup('name') \
            .add_with_lookup('value') \
            .build()
