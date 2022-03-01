"""
byceps.services.party.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
import dataclasses
from datetime import date, datetime, timedelta
from typing import Optional, Union

from sqlalchemy import select

from ...database import db, paginate, Pagination
from ...typing import BrandID, PartyID

from ..brand.dbmodels.brand import Brand as DbBrand
from ..brand import service as brand_service

from .dbmodels.party import Party as DbParty
from .dbmodels.setting import Setting as DbSetting
from .transfer.models import Party, PartyWithBrand


class UnknownPartyId(Exception):
    pass


def create_party(
    party_id: PartyID,
    brand_id: BrandID,
    title: str,
    starts_at: datetime,
    ends_at: datetime,
    *,
    max_ticket_quantity: Optional[int] = None,
) -> Party:
    """Create a party."""
    party = DbParty(
        party_id,
        brand_id,
        title,
        starts_at,
        ends_at,
        max_ticket_quantity=max_ticket_quantity,
    )

    db.session.add(party)
    db.session.commit()

    return _db_entity_to_party(party)


def update_party(
    party_id: PartyID,
    title: str,
    starts_at: datetime,
    ends_at: datetime,
    max_ticket_quantity: Optional[int],
    ticket_management_enabled: bool,
    seat_management_enabled: bool,
    canceled: bool,
    archived: bool,
) -> Party:
    """Update a party."""
    party = db.session.get(DbParty, party_id)

    if party is None:
        raise UnknownPartyId(party_id)

    party.title = title
    party.starts_at = starts_at
    party.ends_at = ends_at
    party.max_ticket_quantity = max_ticket_quantity
    party.ticket_management_enabled = ticket_management_enabled
    party.seat_management_enabled = seat_management_enabled
    party.canceled = canceled
    party.archived = archived

    db.session.commit()

    return _db_entity_to_party(party)


def delete_party(party_id: PartyID) -> None:
    """Delete a party."""
    db.session.query(DbSetting) \
        .filter_by(party_id=party_id) \
        .delete()

    db.session.query(DbParty) \
        .filter_by(id=party_id) \
        .delete()

    db.session.commit()


def count_parties() -> int:
    """Return the number of parties (of all brands)."""
    return db.session.query(DbParty).count()


def count_parties_for_brand(brand_id: BrandID) -> int:
    """Return the number of parties for that brand."""
    return db.session \
        .query(DbParty) \
        .filter_by(brand_id=brand_id) \
        .count()


def find_party(party_id: PartyID) -> Optional[Party]:
    """Return the party with that id, or `None` if not found."""
    party = db.session.get(DbParty, party_id)

    if party is None:
        return None

    return _db_entity_to_party(party)


def get_party(party_id: PartyID) -> Party:
    """Return the party with that id, or `None` if not found."""
    party = find_party(party_id)

    if party is None:
        raise UnknownPartyId(party_id)

    return party


def get_all_parties() -> list[Party]:
    """Return all parties."""
    parties = db.session.query(DbParty).all()

    return [_db_entity_to_party(party) for party in parties]


def get_all_parties_with_brands() -> list[PartyWithBrand]:
    """Return all parties."""
    parties = db.session \
        .query(DbParty) \
        .options(db.joinedload(DbParty.brand)) \
        .all()

    return [_db_entity_to_party_with_brand(party) for party in parties]


def get_active_parties(
    brand_id: Optional[BrandID] = None, *, include_brands: bool = False
) -> list[Union[Party, PartyWithBrand]]:
    """Return active (i.e. non-canceled, non-archived) parties."""
    query = db.session.query(DbParty)

    if brand_id is not None:
        query = query.filter_by(brand_id=brand_id)

    if include_brands:
        query = query.options(db.joinedload(DbParty.brand))

    parties = query \
        .filter_by(canceled=False) \
        .filter_by(archived=False) \
        .order_by(DbParty.starts_at) \
        .all()

    if include_brands:
        transform = _db_entity_to_party_with_brand
    else:
        transform = _db_entity_to_party

    return [transform(party) for party in parties]


def get_archived_parties_for_brand(brand_id: BrandID) -> list[Party]:
    """Return archived parties for that brand."""
    parties = db.session \
        .query(DbParty) \
        .filter_by(brand_id=brand_id) \
        .filter_by(archived=True) \
        .order_by(DbParty.starts_at.desc()) \
        .all()

    return [_db_entity_to_party(party) for party in parties]


def get_parties(party_ids: set[PartyID]) -> list[Party]:
    """Return the parties with those IDs."""
    if not party_ids:
        return []

    parties = db.session \
        .query(DbParty) \
        .filter(DbParty.id.in_(party_ids)) \
        .all()

    return [_db_entity_to_party(party) for party in parties]


def get_parties_for_brand(brand_id: BrandID) -> list[Party]:
    """Return the parties for that brand."""
    parties = db.session \
        .query(DbParty) \
        .filter_by(brand_id=brand_id) \
        .all()

    return [_db_entity_to_party(party) for party in parties]


def get_parties_for_brand_paginated(
    brand_id: BrandID, page: int, per_page: int
) -> Pagination:
    """Return the parties for that brand to show on the specified page."""
    items_query = select(DbParty) \
        .filter_by(brand_id=brand_id) \
        .order_by(DbParty.starts_at.desc())

    count_query = select(db.func.count(DbParty.id)) \
        .filter_by(brand_id=brand_id)

    return paginate(
        items_query,
        count_query,
        page,
        per_page,
        scalar_result=True,
        item_mapper=_db_entity_to_party,
    )


def get_party_count_by_brand_id() -> dict[BrandID, int]:
    """Return party count (including 0) per brand, indexed by brand ID."""
    brand_ids_and_party_counts = db.session \
        .query(
            DbBrand.id,
            db.func.count(DbParty.id)
        ) \
        .outerjoin(DbParty) \
        .group_by(DbBrand.id) \
        .all()

    return dict(brand_ids_and_party_counts)


def _db_entity_to_party(party: DbParty) -> Party:
    return Party(
        id=party.id,
        brand_id=party.brand_id,
        title=party.title,
        starts_at=party.starts_at,
        ends_at=party.ends_at,
        max_ticket_quantity=party.max_ticket_quantity,
        ticket_management_enabled=party.ticket_management_enabled,
        seat_management_enabled=party.seat_management_enabled,
        canceled=party.canceled,
        archived=party.archived,
    )


def _db_entity_to_party_with_brand(party_entity: DbParty) -> PartyWithBrand:
    party = _db_entity_to_party(party_entity)
    brand = brand_service._db_entity_to_brand(party_entity.brand)

    party_tuple = dataclasses.astuple(party)
    brand_tuple = (brand,)

    return PartyWithBrand(*(party_tuple + brand_tuple))


def get_party_days(party: Party) -> list[date]:
    """Return the sequence of dates on which the party happens."""
    starts_on = party.starts_at.date()
    ends_on = party.ends_at.date()

    def _generate():
        if starts_on > ends_on:
            raise ValueError('Start date must not be after end date.')

        day_step = timedelta(days=1)
        day = starts_on
        while True:
            yield day
            day += day_step
            if day > ends_on:
                return

    return list(_generate())
