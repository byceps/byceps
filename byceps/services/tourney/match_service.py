"""
byceps.services.tourney.match_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...database import db

from .models.match import Match as DbMatch
from .transfer.models import MatchID


def create_match() -> MatchID:
    """Create a match."""
    match = DbMatch()

    db.session.add(match)
    db.session.commit()

    return match.id


def find_match(match_id: MatchID) -> Optional[DbMatch]:
    """Return the match with that id, or `None` if not found."""
    return DbMatch.query.get(match_id)
