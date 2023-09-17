"""
byceps.services.tourney.dbmodels.match
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.tourney.models import MatchID
from byceps.util.uuid import generate_uuid7


class DbMatch(db.Model):
    """A match between two opponents."""

    __tablename__ = 'tourney_matches'

    id: Mapped[MatchID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
