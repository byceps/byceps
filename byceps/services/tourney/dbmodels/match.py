"""
byceps.services.tourney.dbmodels.match
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.tourney.models import MatchID


class DbMatch(db.Model):
    """A match between two opponents."""

    __tablename__ = 'tourney_matches'

    id: Mapped[MatchID] = mapped_column(db.Uuid, primary_key=True)

    def __init__(self, match_id: MatchID) -> None:
        self.id = match_id
