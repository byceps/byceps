"""
byceps.services.language.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...database import db


class DbLanguage(db.Model):
    """A language.

    The code can be just `en` or `de`, but also `en-gb` or `de-de`.
    """

    __tablename__ = 'languages'

    code = db.Column(db.UnicodeText, primary_key=True)

    def __init__(self, code: str) -> None:
        self.code = code
