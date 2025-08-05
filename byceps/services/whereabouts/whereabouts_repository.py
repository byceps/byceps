"""
byceps.services.whereabouts.whereabouts_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import select

from byceps.database import db, execute_upsert
from byceps.services.party.models import PartyID
from byceps.services.user.models.user import UserID

from .dbmodels import (
    DbWhereabouts,
    DbWhereaboutsStatus,
    DbWhereaboutsUpdate,
)
from .models import (
    Whereabouts,
    WhereaboutsID,
    WhereaboutsStatus,
    WhereaboutsUpdate,
)


# -------------------------------------------------------------------- #
# whereabouts


def create_whereabouts(whereabouts: Whereabouts) -> None:
    """Create whereabouts."""
    db_whereabouts = DbWhereabouts(
        whereabouts.id,
        whereabouts.party.id,
        whereabouts.name,
        whereabouts.description,
        whereabouts.position,
        whereabouts.hidden_if_empty,
        whereabouts.secret,
    )

    db.session.add(db_whereabouts)
    db.session.commit()


def update_whereabouts(whereabouts: Whereabouts) -> None:
    """Update whereabouts."""
    db_whereabouts = find_db_whereabouts(whereabouts.id)

    db_whereabouts.name = whereabouts.name
    db_whereabouts.description = whereabouts.description
    db_whereabouts.hidden_if_empty = whereabouts.hidden_if_empty
    db_whereabouts.secret = whereabouts.secret

    db.session.commit()


def find_db_whereabouts(whereabouts_id: WhereaboutsID) -> DbWhereabouts | None:
    """Return whereabouts, if found."""
    return db.session.get(DbWhereabouts, whereabouts_id)


def find_db_whereabouts_by_name(
    party_id: PartyID, name: str
) -> DbWhereabouts | None:
    """Return whereabouts wi, if found."""
    return db.session.scalars(
        select(DbWhereabouts).filter_by(party_id=party_id).filter_by(name=name)
    ).one_or_none()


def get_db_whereabouts_list(party_id: PartyID) -> list[DbWhereabouts]:
    """Return possible whereabouts."""
    return db.session.scalars(
        select(DbWhereabouts).filter_by(party_id=party_id)
    ).all()


# -------------------------------------------------------------------- #
# status


def persist_update(
    status: WhereaboutsStatus, update: WhereaboutsUpdate
) -> None:
    # status
    table = DbWhereaboutsStatus.__table__
    identifier = {
        'user_id': status.user.id,
    }
    replacement = {
        'whereabouts_id': status.whereabouts_id,
        'set_at': status.set_at,
    }
    execute_upsert(table, identifier, replacement)

    # update
    db_update = DbWhereaboutsUpdate(
        update.id,
        update.user.id,
        update.whereabouts_id,
        update.created_at,
        update.source_address,
    )
    db.session.add(db_update)

    db.session.commit()


def find_db_status(
    user_id: UserID, party_id: PartyID
) -> DbWhereaboutsStatus | None:
    """Return user's status for the party, if known."""
    return db.session.scalars(
        select(DbWhereaboutsStatus)
        .join(DbWhereabouts)
        .filter(DbWhereaboutsStatus.user_id == user_id)
        .filter(DbWhereabouts.party_id == party_id)
    ).one_or_none()


def get_db_statuses(party_id: PartyID) -> list[DbWhereaboutsStatus]:
    """Return user statuses."""
    return db.session.scalars(
        select(DbWhereaboutsStatus)
        .join(DbWhereabouts)
        .filter(DbWhereabouts.party_id == party_id)
    ).all()
