"""
byceps.services.whereabouts.whereabouts_sound_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.user.models.user import UserID

from .dbmodels import DbWhereaboutsUserSound
from .models import WhereaboutsUserSound


def create_user_sound(user_sound: WhereaboutsUserSound) -> None:
    """Set a users-specific sound."""
    db_user_sound = DbWhereaboutsUserSound(user_sound.user.id, user_sound.name)

    db.session.add(db_user_sound)
    db.session.commit()


def update_user_sound(user_sound: WhereaboutsUserSound) -> None:
    """Update a users-specific sound."""
    db_user_sound = find_sound_for_user(user_sound.user.id)

    db_user_sound.name = user_sound.name

    db.session.commit()


def delete_user_sound(user_id: UserID) -> None:
    """Delete a users-specific sound."""
    db.session.execute(
        delete(DbWhereaboutsUserSound).filter_by(user_id=user_id)
    )

    db.session.commit()


def find_sound_for_user(user_id: UserID) -> DbWhereaboutsUserSound | None:
    """Find a sound specific for this user."""
    return db.session.scalars(
        select(DbWhereaboutsUserSound).filter_by(user_id=user_id)
    ).one_or_none()


def get_all_user_sounds() -> list[DbWhereaboutsUserSound]:
    """Return all user sounds."""
    return db.session.scalars(select(DbWhereaboutsUserSound)).all()
