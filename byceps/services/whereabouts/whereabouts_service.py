"""
byceps.services.whereabouts.whereabouts_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
import dataclasses
from datetime import datetime, timedelta

from byceps.services.party import party_service
from byceps.services.party.models import Party
from byceps.services.user import user_service
from byceps.services.user.models import User

from . import (
    whereabouts_client_repository,
    whereabouts_domain_service,
    whereabouts_repository,
)
from .dbmodels import DbWhereabouts, DbWhereaboutsStatus
from .events import WhereaboutsStatusUpdatedEvent
from .models import (
    IPAddress,
    Overview,
    OverviewStatus,
    OverviewWhereabouts,
    Whereabouts,
    WhereaboutsClient,
    WhereaboutsID,
    WhereaboutsStatus,
    WhereaboutsUpdate,
)


# -------------------------------------------------------------------- #
# whereabouts


def copy_whereabouts_list(source_party: Party, target_party: Party) -> None:
    """Copy all whereabouts from one party to another."""
    for whereabouts in get_whereabouts_list(source_party):
        create_whereabouts(
            target_party,
            whereabouts.name,
            whereabouts.description,
            position=whereabouts.position,
            hidden_if_empty=whereabouts.hidden_if_empty,
            secret=whereabouts.secret,
        )


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
    if position is not None:
        next_position = position
    else:
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
    db_whereabouts = whereabouts_repository.find_whereabouts(whereabouts_id)

    if db_whereabouts is None:
        return None

    party = party_service.get_party(db_whereabouts.party_id)

    return _db_entity_to_whereabouts(db_whereabouts, party)


def find_whereabouts_by_name(party: Party, name: str) -> Whereabouts | None:
    """Return whereabouts wi, if found."""
    db_whereabouts = whereabouts_repository.find_whereabouts_by_name(
        party.id, name
    )

    if db_whereabouts is None:
        return None

    return _db_entity_to_whereabouts(db_whereabouts, party)


def get_whereabouts_list(party: Party) -> list[Whereabouts]:
    """Return possible whereabouts."""
    db_whereabouts_list = whereabouts_repository.get_whereabouts_list(party.id)

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
    db_status = whereabouts_repository.find_status(user.id, party.id)

    if db_status is None:
        return None

    user = user_service.get_user(db_status.user_id, include_avatar=True)

    return _db_entity_to_status(db_status, user)


def get_statuses(party: Party) -> list[WhereaboutsStatus]:
    """Return user statuses."""
    db_statuses = whereabouts_repository.get_statuses(party.id)

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


# -------------------------------------------------------------------- #
# overview


STALE_THRESHOLD = timedelta(hours=12)


def get_whereabouts_list_with_statuses(
    party: Party,
) -> list[OverviewWhereabouts]:
    """Return whereabouts and the related statuses for the party."""
    whereabouts_list = get_whereabouts_list(party)

    statuses = get_statuses(party)

    now = datetime.utcnow()

    def is_status_stale(status: WhereaboutsStatus) -> bool:
        return (now - STALE_THRESHOLD) > status.set_at

    def to_overview_status(status: WhereaboutsStatus) -> OverviewStatus:
        return OverviewStatus(
            user=status.user,
            set_at=status.set_at,
            stale=is_status_stale(status),
        )

    def to_overview_whereabouts(
        whereabouts: Whereabouts, statuses: list[WhereaboutsStatus]
    ) -> OverviewWhereabouts:
        overview_statuses = [to_overview_status(status) for status in statuses]

        return OverviewWhereabouts(
            name=whereabouts.name,
            description=whereabouts.description,
            position=whereabouts.position,
            hidden_if_empty=whereabouts.hidden_if_empty,
            secret=whereabouts.secret,
            statuses=overview_statuses,
        )

    statuses_by_whereabouts = defaultdict(list)
    for status in statuses:
        statuses_by_whereabouts[status.whereabouts_id].append(status)

    overview_whereabouts_list = []
    for whereabouts in whereabouts_list:
        statuses = statuses_by_whereabouts[whereabouts.id]

        overview_whereabouts = to_overview_whereabouts(whereabouts, statuses)

        overview_whereabouts_list.append(overview_whereabouts)

    return overview_whereabouts_list


def get_overview(party: Party) -> Overview:
    """Return an overview about whereabouts and statuses for the party."""
    overview_whereabouts_list = get_whereabouts_list_with_statuses(party)

    recent_whereabouts_list, stale_statuses = separate_stale_statuses(
        overview_whereabouts_list
    )

    return Overview(
        whereabouts_list=overview_whereabouts_list,
        stale_statuses=stale_statuses,
    )


def separate_stale_statuses(
    whereabouts_list: list[OverviewWhereabouts],
) -> tuple[list[OverviewWhereabouts], list[OverviewStatus]]:
    """Separate stale statuses from the recent ones."""
    whereabouts_list_with_recent_statuses = []
    stale_statuses = []

    for whereabouts in whereabouts_list:
        recent_statuses = []

        for status in whereabouts.statuses:
            collection = stale_statuses if status.stale else recent_statuses
            collection.append(status)

        updated_whereabouts = dataclasses.replace(
            whereabouts, statuses=recent_statuses
        )

        whereabouts_list_with_recent_statuses.append(updated_whereabouts)

    return whereabouts_list_with_recent_statuses, stale_statuses
