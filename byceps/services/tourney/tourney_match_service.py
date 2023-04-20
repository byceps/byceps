"""
byceps.services.tourney.tourney_match_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations


from sqlalchemy import delete

from byceps.database import db

from .dbmodels.match import DbMatch
from .models import Match, MatchID


def create_match() -> Match:
    """Create a match."""
    db_match = DbMatch()

    db.session.add(db_match)
    db.session.commit()

    return _db_entity_to_match(db_match)


def delete_match(match_id: MatchID) -> None:
    """Delete a match."""
    match = find_match(match_id)
    if match is None:
        raise ValueError(f'Unknown match ID "{match_id}"')

    db.session.execute(delete(DbMatch).filter_by(id=match.id))
    db.session.commit()


def find_match(match_id: MatchID) -> Match | None:
    """Return the match with that id, or `None` if not found."""
    db_match = db.session.get(DbMatch, match_id)

    if db_match is None:
        return None

    return _db_entity_to_match(db_match)


def _db_entity_to_match(db_match: DbMatch) -> Match:
    return Match(id=db_match.id)
