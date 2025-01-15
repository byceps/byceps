"""
byceps.services.language.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db


class DbLanguage(db.Model):
    """A language.

    The code can be just `en` or `de`, but also `en-gb` or `de-de`.
    """

    __tablename__ = 'languages'

    code: Mapped[str] = mapped_column(db.UnicodeText, primary_key=True)

    def __init__(self, code: str) -> None:
        self.code = code
