"""
byceps.services.global_setting.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.util.instances import ReprBuilder


class DbGlobalSetting(db.Model):
    """A global setting."""

    __tablename__ = 'global_settings'

    name: Mapped[str] = mapped_column(db.UnicodeText, primary_key=True)
    value: Mapped[str] = mapped_column(db.UnicodeText)

    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('name')
            .add_with_lookup('value')
            .build()
        )
