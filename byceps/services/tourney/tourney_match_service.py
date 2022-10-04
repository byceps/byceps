"""
byceps.services.tourney.tourney_match_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...database import db

from .dbmodels.match import DbMatch
from .transfer.models import Match, MatchID


def create_match() -> Match:
    """Create a match."""
    match = DbMatch()

    db.session.add(match)
    db.session.commit()

    return _db_entity_to_match(match)


def delete_match(match_id: MatchID) -> None:
    """Delete a match."""
    match = find_match(match_id)
    if match is None:
        raise ValueError(f'Unknown match ID "{match_id}"')

    db.session.query(DbMatch) \
        .filter_by(id=match_id) \
        .delete()

    db.session.commit()


def find_match(match_id: MatchID) -> Optional[Match]:
    """Return the match with that id, or `None` if not found."""
    match = db.session.get(DbMatch, match_id)

    if match is None:
        return None

    return _db_entity_to_match(match)


def _db_entity_to_match(match: DbMatch) -> Match:
    return Match(match.id)
