"""
byceps.services.tourney.tourney_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.party.models import Party, PartyID
from byceps.services.tourney.log import tourney_log_service
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result

from . import tourney_category_service, tourney_domain_service
from .dbmodels.participant import DbParticipant
from .dbmodels.tourney import DbTourney
from .dbmodels.tourney_category import DbTourneyCategory
from .events import (
    TourneyCreatedEvent,
    TourneyRegistrationClosedEvent,
    TourneyRegistrationOpenedEvent,
)
from .models import (
    Tourney,
    TourneyCategory,
    TourneyCategoryID,
    TourneyID,
    TourneyWithCategory,
)


def create_tourney(
    party: Party,
    creator: User,
    title: str,
    category: TourneyCategory,
    team_size: int,
    max_participant_count: int,
    starts_at: datetime,
    *,
    subtitle: str | None = None,
    logo_url: str | None = None,
    registration_open: bool = False,
) -> tuple[Tourney, TourneyCreatedEvent]:
    """Create a tourney."""
    tourney, event, log_entry = tourney_domain_service.create_tourney(
        party,
        creator,
        title,
        category,
        team_size,
        max_participant_count,
        starts_at,
        subtitle=subtitle,
        logo_url=logo_url,
        registration_open=registration_open,
    )

    _persist_tourney_creation(tourney)

    tourney_log_service.persist_entry(log_entry)

    return tourney, event


def _persist_tourney_creation(tourney: Tourney) -> None:
    db_tourney = DbTourney(
        tourney.id,
        tourney.party_id,
        tourney.title,
        tourney.category_id,
        tourney.team_size,
        tourney.max_participant_count,
        tourney.starts_at,
        subtitle=tourney.subtitle,
        logo_url=tourney.logo_url,
        registration_open=tourney.registration_open,
    )

    db.session.add(db_tourney)
    db.session.commit()


def update_tourney(
    tourney_id: TourneyID,
    title: str,
    subtitle: str | None,
    logo_url: str | None,
    category_id: TourneyCategoryID,
    max_participant_count: int,
    starts_at: datetime,
) -> Tourney:
    """Update tourney."""
    db_tourney = _get_db_tourney(tourney_id)

    db_tourney.title = title
    db_tourney.subtitle = subtitle
    db_tourney.logo_url = logo_url
    db_tourney.category_id = category_id
    db_tourney.max_participant_count = max_participant_count
    db_tourney.starts_at = starts_at

    db.session.commit()

    return _db_entity_to_tourney(db_tourney)


def open_registration(
    tourney: Tourney, initiator: User
) -> Result[tuple[Tourney, TourneyRegistrationOpenedEvent], str]:
    """Open the registration for a tourney."""
    db_tourney = _get_db_tourney(tourney.id)

    result = tourney_domain_service.open_registration(tourney, initiator)
    match result:
        case Err(e):
            return Err(e)

    updated_tourney, event, log_entry = result.unwrap()

    db_tourney.registration_open = updated_tourney.registration_open
    db.session.commit()

    tourney_log_service.persist_entry(log_entry)

    return Ok((updated_tourney, event))


def close_registration(
    tourney: Tourney, initiator: User
) -> Result[tuple[Tourney, TourneyRegistrationClosedEvent], str]:
    """Close the registration for a tourney."""
    db_tourney = _get_db_tourney(tourney.id)

    result = tourney_domain_service.close_registration(tourney, initiator)
    match result:
        case Err(e):
            return Err(e)

    updated_tourney, event, log_entry = result.unwrap()

    db_tourney.registration_open = updated_tourney.registration_open
    db.session.commit()

    tourney_log_service.persist_entry(log_entry)

    return Ok((updated_tourney, event))


def delete_tourney(tourney_id: TourneyID) -> None:
    """Delete a tourney."""
    tourney = get_tourney(tourney_id)

    db.session.execute(delete(DbTourney).filter_by(id=tourney.id))
    db.session.commit()


def find_tourney(tourney_id: TourneyID) -> Tourney | None:
    """Return the tourney with that id, or `None` if not found."""
    db_tourney = _find_db_tourney(tourney_id)

    if db_tourney is None:
        return None

    return _db_entity_to_tourney(db_tourney)


def _find_db_tourney(tourney_id: TourneyID) -> DbTourney | None:
    return db.session.get(DbTourney, tourney_id)


def get_tourney(tourney_id: TourneyID) -> Tourney:
    """Return the tourney with that ID.

    Raise an exception if not found.
    """
    tourney = find_tourney(tourney_id)

    if tourney is None:
        raise ValueError(f'Unknown tourney ID "{tourney_id}"')

    return tourney


def _get_db_tourney(tourney_id: TourneyID) -> DbTourney:
    db_tourney = _find_db_tourney(tourney_id)

    if db_tourney is None:
        raise ValueError(f'Unknown tourney ID "{tourney_id}"')

    return db_tourney


def find_tourney_with_category(
    tourney_id: TourneyID,
) -> TourneyWithCategory | None:
    """Return the tourney with that id, or `None` if not found."""
    row = _find_db_tourney_with_category(tourney_id)

    if row is None:
        return None

    db_tourney, db_category, participant_count = row

    return _to_tourney_with_category(db_tourney, db_category, participant_count)


def _find_db_tourney_with_category(
    tourney_id: TourneyID,
) -> tuple[DbTourney, DbTourneyCategory, int] | None:
    return (
        db.session.execute(
            select(
                DbTourney, DbTourneyCategory, db.func.count(DbParticipant.id)
            )
            .join(DbTourneyCategory)
            .join(DbParticipant, isouter=True)
            .filter(DbTourney.id == tourney_id)
            .group_by(DbTourney.id, DbTourneyCategory)
        )
        .tuples()
        .one_or_none()
    )


def get_tourneys_for_party(party_id: PartyID) -> list[TourneyWithCategory]:
    """Return the tourneys for that party."""
    rows = db.session.execute(
        select(DbTourney, DbTourneyCategory, db.func.count(DbParticipant.id))
        .join(DbTourneyCategory)
        .join(DbParticipant, isouter=True)
        .filter(DbTourney.party_id == party_id)
        .group_by(DbTourney.id, DbTourneyCategory)
    ).all()

    return [
        _to_tourney_with_category(db_tourney, db_category, participant_count)
        for db_tourney, db_category, participant_count in rows
    ]


def _db_entity_to_tourney(
    db_tourney: DbTourney,
    current_participant_count: int = -1,
) -> Tourney:
    return Tourney(
        id=db_tourney.id,
        party_id=db_tourney.party_id,
        title=db_tourney.title,
        subtitle=db_tourney.subtitle,
        logo_url=db_tourney.logo_url,
        category_id=db_tourney.category_id,
        team_size=db_tourney.team_size,
        current_participant_count=current_participant_count,
        max_participant_count=db_tourney.max_participant_count,
        starts_at=db_tourney.starts_at,
        registration_open=db_tourney.registration_open,
    )


def _to_tourney_with_category(
    db_tourney: DbTourney,
    db_category: DbTourneyCategory,
    current_participant_count: int = -1,
) -> TourneyWithCategory:
    tourney = _db_entity_to_tourney(db_tourney, current_participant_count)
    category = tourney_category_service._db_entity_to_category(db_category)

    return TourneyWithCategory.from_tourney_and_category(
        tourney, category, current_participant_count
    )
