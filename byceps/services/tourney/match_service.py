"""
byceps.services.tourney.match_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db
from ...typing import UserID

from .models.match import Match, MatchID, MatchComment


# -------------------------------------------------------------------- #
# matches


def create_match() -> MatchID:
    """Create a match."""
    match = Match()

    db.session.add(match)
    db.session.commit()

    return match.id


def find_match(match_id: MatchID) -> Optional[Match]:
    """Return the match with that id, or `None` if not found."""
    return Match.query.get(match_id)


# -------------------------------------------------------------------- #
# comments


def get_comments(match_id: MatchID) -> Sequence[MatchComment]:
    """Return comments on the match, ordered chronologically."""
    return MatchComment.query \
        .for_match(match_id) \
        .options(
            db.joinedload(MatchComment.created_by),
        ) \
        .order_by(MatchComment.created_at) \
        .all()


def create_comment(match_id: MatchID, creator_id: UserID, body: str
                  ) -> MatchComment:
    """Create a comment on a match."""
    comment = MatchComment(match_id, creator_id, body)

    db.session.add(comment)
    db.session.commit()

    return comment
