"""
byceps.services.party.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set

from flask_sqlalchemy import Pagination

from ...database import db
from ...typing import BrandID, PartyID

from ..brand.models.brand import Brand as DbBrand

from .models.party import Party as DbParty
from .models.setting import Setting as DbSetting
from .transfer.models import Party, PartySetting


class UnknownPartyId(Exception):
    pass


def create_party(party_id: PartyID, brand_id: BrandID, title: str,
                 starts_at: datetime, ends_at: datetime) -> Party:
    """Create a party."""
    party = DbParty(party_id, brand_id, title, starts_at, ends_at)

    db.session.add(party)
    db.session.commit()

    return _db_entity_to_party(party)


def update_party(party_id: PartyID, title: str, starts_at: datetime,
                 ends_at: datetime, is_archived: bool) -> Party:
    """Update a party."""
    party = DbParty.query.get(party_id)

    if party is None:
        raise UnknownPartyId(party_id)

    party.title = title
    party.starts_at = starts_at
    party.ends_at = ends_at
    party.is_archived = is_archived

    db.session.commit()

    return _db_entity_to_party(party)


def count_parties() -> int:
    """Return the number of parties (of all brands)."""
    return DbParty.query.count()


def count_parties_for_brand(brand_id: BrandID) -> int:
    """Return the number of parties for that brand."""
    return DbParty.query \
        .filter_by(brand_id=brand_id) \
        .count()


def find_party(party_id: PartyID) -> Optional[DbParty]:
    """Return the party with that id, or `None` if not found."""
    return DbParty.query.get(party_id)


def get_all_parties_with_brands() -> List[DbParty]:
    """Return all parties."""
    return DbParty.query \
        .options(db.joinedload('brand')) \
        .all()


def get_active_parties(brand_id: Optional[BrandID]=None) -> List[Party]:
    """Return active (i.e. non-archived) parties."""
    query = DbParty.query

    if brand_id is not None:
        query = query \
            .filter_by(brand_id=brand_id)

    parties = query \
        .filter_by(is_archived=False) \
        .order_by(DbParty.starts_at) \
        .all()

    return [_db_entity_to_party(party) for party in parties]


def get_archived_parties_for_brand(brand_id: BrandID) -> List[Party]:
    """Return archived parties for that brand."""
    parties = DbParty.query \
        .filter_by(brand_id=brand_id) \
        .filter_by(is_archived=True) \
        .order_by(DbParty.starts_at.desc()) \
        .all()

    return [_db_entity_to_party(party) for party in parties]


def get_parties(party_ids: Set[PartyID]) -> List[Party]:
    """Return the parties with those IDs."""
    if not party_ids:
        return []

    parties = DbParty.query \
        .filter(DbParty.id.in_(party_ids)) \
        .all()

    return [_db_entity_to_party(party) for party in parties]


def get_parties_for_brand_paginated(brand_id: BrandID, page: int,
                                    per_page: int) -> Pagination:
    """Return the parties for that brand to show on the specified page."""
    return DbParty.query \
        .filter_by(brand_id=brand_id) \
        .order_by(DbParty.starts_at.desc()) \
        .paginate(page, per_page)


def get_party_count_by_brand_id() -> Dict[BrandID, int]:
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


def find_setting(party_id: PartyID, name: str) -> Optional[PartySetting]:
    """Return the setting for that party and with that name, or `None`
    if not found.
    """
    setting = DbSetting.query.get((party_id, name))

    if setting is None:
        return None

    return _db_entity_to_party_setting(setting)


def _db_entity_to_party(party: DbParty) -> Party:
    return Party(
        party.id,
        party.brand_id,
        party.title,
        party.starts_at,
        party.ends_at,
        party.is_archived,
    )


def _db_entity_to_party_setting(setting: DbSetting) -> PartySetting:
    return PartySetting(
        setting.party_id,
        setting.name,
        setting.value,
    )
