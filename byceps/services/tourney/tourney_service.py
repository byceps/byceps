"""
byceps.services.tourney.tourney_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import List, Optional

from ...database import db
from ...typing import PartyID, UserID

from .models.participant import Participant as DbParticipant
from .models.tourney import Tourney as DbTourney
from .models.tourney_category import TourneyCategory as DbTourneyCategory
from .transfer.models import Tourney


def find_tourney(tourney_id: int) -> Optional[Tourney]:
    """Return the tourney with that id, or `None` if not found."""
    tourney = DbTourney.query.get(tourney_id)

    if tourney is None:
        return None

    return _db_entity_to_tourney(tourney)


def get_tourneys_for_party(party_id: PartyID) -> List[Tourney]:
    """Return the tourneys for that party."""
    rows = db.session \
        .query(DbTourney, db.func.count(DbParticipant.id)) \
        .join(DbTourneyCategory) \
        .join(DbParticipant, isouter=True) \
        .filter(DbTourneyCategory.party_id == party_id) \
        .group_by(DbTourney.id) \
        .all()

    return [_db_entity_to_tourney(row[0], row[1]) for row in rows]


def _db_entity_to_tourney(
    tourney: DbTourney, current_participant_count: int = -1
) -> Tourney:
    return Tourney(
        tourney.id,
        tourney.category_id,
        tourney.title,
        tourney.subtitle,
        tourney.logo_url,
        current_participant_count,
        tourney.max_participant_count,
        tourney.starts_at,
    )
