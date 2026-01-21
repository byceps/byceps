"""
byceps.services.board.dbmodels.board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.board.models import BoardID
from byceps.services.brand.models import BrandID


class DbBoard(db.Model):
    """A board."""

    __tablename__ = 'boards'

    id: Mapped[BoardID] = mapped_column(db.UnicodeText, primary_key=True)
    brand_id: Mapped[BrandID] = mapped_column(
        db.UnicodeText, db.ForeignKey('brands.id'), index=True
    )
    access_restricted: Mapped[bool] = mapped_column(default=False)

    def __init__(self, board_id: BoardID, brand_id: BrandID) -> None:
        self.id = board_id
        self.brand_id = brand_id
