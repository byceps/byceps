"""
byceps.services.tourney.match_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...database import db

from .models.match import Match as DbMatch
from .transfer.models import Match, MatchID


def create_match() -> Match:
    """Create a match."""
    match = DbMatch()

    db.session.add(match)
    db.session.commit()

    return _db_entity_to_match(match)


def find_match(match_id: MatchID) -> Optional[Match]:
    """Return the match with that id, or `None` if not found."""
    match = DbMatch.query.get(match_id)

    if match is None:
        return None

    return _db_entity_to_match(match)


def _db_entity_to_match(match: DbMatch) -> Match:
    return Match(match.id)
