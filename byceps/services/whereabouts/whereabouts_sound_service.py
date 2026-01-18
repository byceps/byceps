"""
byceps.services.whereabouts.whereabouts_sound_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses

from byceps.services.user import user_service
from byceps.services.user.models.user import User, UserID

from . import whereabouts_sound_repository
from .dbmodels import DbWhereaboutsUserSound
from .models import WhereaboutsUserSound


def create_user_sound(user: User, name: str) -> WhereaboutsUserSound:
    """Set a users-specific sound."""
    user_sound = WhereaboutsUserSound(user=user, name=name)

    whereabouts_sound_repository.create_user_sound(user_sound)

    return user_sound


def update_user_sound(
    user_sound: WhereaboutsUserSound, name: str
) -> WhereaboutsUserSound:
    """Update a users-specific sound."""
    updated_user_sound = dataclasses.replace(user_sound, name=name)

    whereabouts_sound_repository.update_user_sound(updated_user_sound)

    return updated_user_sound


def delete_user_sound(user_id: UserID) -> None:
    """Delete a users-specific sound."""
    whereabouts_sound_repository.delete_user_sound(user_id)


def find_sound_for_user(user_id: UserID) -> WhereaboutsUserSound | None:
    """Find a sound specific for this user."""
    db_user_sound = whereabouts_sound_repository.find_sound_for_user(user_id)

    if db_user_sound is None:
        return None

    user = user_service.get_user(db_user_sound.user_id, include_avatar=True)

    return _db_entity_to_user_sound(db_user_sound, user)


def get_all_user_sounds() -> list[WhereaboutsUserSound]:
    """Return all user sounds."""
    db_user_sounds = whereabouts_sound_repository.get_all_user_sounds()

    user_ids = {db_user_sound.user_id for db_user_sound in db_user_sounds}
    users_by_id = user_service.get_users_indexed_by_id(
        user_ids, include_avatars=True
    )

    return [
        _db_entity_to_user_sound(
            db_user_sound, users_by_id[db_user_sound.user_id]
        )
        for db_user_sound in db_user_sounds
    ]


def _db_entity_to_user_sound(
    db_user_sound: DbWhereaboutsUserSound, user: User
) -> WhereaboutsUserSound:
    return WhereaboutsUserSound(
        user=user,
        name=db_user_sound.name,
    )
