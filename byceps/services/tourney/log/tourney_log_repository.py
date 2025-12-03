"""
byceps.services.tourney.log.tourney_log_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from sqlalchemy import select

from byceps.database import db
from byceps.services.tourney.models import TourneyID
from byceps.services.user.dbmodels.user import DbUser

from .dbmodels import DbTourneyLogEntry


def persist_tourney_entry(db_entry: DbTourneyLogEntry) -> None:
    """Store a log entry for a tourney."""
    db.session.add(db_entry)
    db.session.commit()


def get_entries_for_tourney(
    tourney_id: TourneyID,
) -> Sequence[tuple[DbTourneyLogEntry, DbUser]]:
    """Return the log entries for that tourney."""
    return (
        db.session.execute(
            select(DbTourneyLogEntry, DbUser)
            .join(DbUser)
            .filter(DbTourneyLogEntry.tourney_id == tourney_id)
            .order_by(DbTourneyLogEntry.occurred_at)
        )
        .tuples()
        .all()
    )
