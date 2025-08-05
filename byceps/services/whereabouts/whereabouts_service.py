"""
byceps.services.whereabouts.whereabouts_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses

from byceps.services.party import party_service
from byceps.services.party.models import Party
from byceps.services.user import user_service
from byceps.services.user.models.user import User

from . import (
    whereabouts_client_repository,
    whereabouts_domain_service,
    whereabouts_repository,
)
from .dbmodels import (
    DbWhereabouts,
    DbWhereaboutsStatus,
    DbWhereaboutsUpdate,
)
from .events import WhereaboutsStatusUpdatedEvent
from .models import (
    IPAddress,
    Whereabouts,
    WhereaboutsClient,
    WhereaboutsID,
    WhereaboutsStatus,
    WhereaboutsUpdate,
)


# -------------------------------------------------------------------- #
# whereabouts


def create_whereabouts(
    party: Party,
    name: str,
    description: str,
    *,
    position: int | None = None,
    hidden_if_empty: bool = False,
    secret: bool = False,
) -> Whereabouts:
    """Create whereabouts."""
    if position is None:
        whereabouts_list = get_whereabouts_list(party)
        if whereabouts_list:
            next_position = max(w.position for w in whereabouts_list) + 1
        else:
            next_position = 0

    whereabouts = whereabouts_domain_service.create_whereabouts(
        party,
        name,
        description,
        next_position,
        hidden_if_empty=hidden_if_empty,
        secret=secret,
    )

    whereabouts_repository.create_whereabouts(whereabouts)

    return whereabouts


def update_whereabouts(
    whereabouts: Whereabouts,
    name: str,
    description: str,
    hidden_if_empty: bool,
    secret: bool,
) -> Whereabouts:
    """Update whereabouts."""
    updated_whereabouts = dataclasses.replace(
        whereabouts,
        name=name,
        description=description,
        hidden_if_empty=hidden_if_empty,
        secret=secret,
    )

    whereabouts_repository.update_whereabouts(updated_whereabouts)

    return updated_whereabouts


def find_whereabouts(whereabouts_id: WhereaboutsID) -> Whereabouts | None:
    """Return whereabouts, if found."""
    db_whereabouts = whereabouts_repository.find_db_whereabouts(whereabouts_id)

    if db_whereabouts is None:
        return None

    party = party_service.get_party(db_whereabouts.party_id)

    return _db_entity_to_whereabouts(db_whereabouts, party)


def find_whereabouts_by_name(party: Party, name: str) -> Whereabouts | None:
    """Return whereabouts wi, if found."""
    db_whereabouts = whereabouts_repository.find_db_whereabouts_by_name(
        party.id, name
    )

    if db_whereabouts is None:
        return None

    return _db_entity_to_whereabouts(db_whereabouts, party)


def get_whereabouts_list(party: Party) -> list[Whereabouts]:
    """Return possible whereabouts."""
    db_whereabouts_list = whereabouts_repository.get_db_whereabouts_list(
        party.id
    )

    return [
        _db_entity_to_whereabouts(db_whereabouts, party)
        for db_whereabouts in db_whereabouts_list
    ]


def _db_entity_to_whereabouts(
    db_whereabouts: DbWhereabouts, party: Party
) -> Whereabouts:
    return Whereabouts(
        id=db_whereabouts.id,
        party=party,
        name=db_whereabouts.name,
        description=db_whereabouts.description,
        position=db_whereabouts.position,
        hidden_if_empty=db_whereabouts.hidden_if_empty,
        secret=db_whereabouts.secret,
    )


# -------------------------------------------------------------------- #
# status


def set_status(
    client: WhereaboutsClient,
    user: User,
    whereabouts: Whereabouts,
    *,
    source_address: IPAddress | None = None,
) -> tuple[WhereaboutsStatus, WhereaboutsUpdate, WhereaboutsStatusUpdatedEvent]:
    """Set a user's whereabouts."""
    status, update, event = whereabouts_domain_service.set_status(
        user, whereabouts, source_address=source_address
    )

    whereabouts_repository.persist_update(status, update)

    whereabouts_client_repository.update_liveliness_status(
        client.id, True, event.occurred_at
    )

    return status, update, event


def find_status(user: User, party: Party) -> WhereaboutsStatus | None:
    """Return user's status for the party, if known."""
    db_status = whereabouts_repository.find_db_status(user.id, party.id)

    if db_status is None:
        return None

    user = user_service.get_user(db_status.user_id, include_avatar=True)

    return _db_entity_to_status(db_status, user)


def get_statuses(party: Party) -> list[WhereaboutsStatus]:
    """Return user statuses."""
    db_statuses = whereabouts_repository.get_db_statuses(party.id)

    user_ids = {db_status.user_id for db_status in db_statuses}
    users_by_id = user_service.get_users_indexed_by_id(
        user_ids, include_avatars=True
    )

    return [
        _db_entity_to_status(db_status, users_by_id[db_status.user_id])
        for db_status in db_statuses
    ]


def _db_entity_to_status(
    db_status: DbWhereaboutsStatus, user: User
) -> WhereaboutsStatus:
    return WhereaboutsStatus(
        user=user,
        whereabouts_id=db_status.whereabouts_id,
        set_at=db_status.set_at,
    )
