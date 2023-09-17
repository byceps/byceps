"""
byceps.services.site.dbmodels.setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.site.models import SiteID
from byceps.util.instances import ReprBuilder


class DbSetting(db.Model):
    """A site-specific setting."""

    __tablename__ = 'site_settings'

    site_id: Mapped[SiteID] = mapped_column(
        db.UnicodeText, db.ForeignKey('sites.id'), primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(db.UnicodeText, primary_key=True)
    value: Mapped[str] = mapped_column(db.UnicodeText)

    def __init__(self, site_id: SiteID, name: str, value: str) -> None:
        self.site_id = site_id
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('site_id')
            .add_with_lookup('name')
            .add_with_lookup('value')
            .build()
        )
