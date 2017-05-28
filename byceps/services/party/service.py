"""
byceps.services.party.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set

from flask_sqlalchemy import Pagination

from ...database import db
from ...typing import BrandID, PartyID

from ..brand.models import Brand

from .models import Party, PartyTuple


class UnknownPartyId(Exception):
    pass


def create_party(party_id: PartyID, brand_id: BrandID, title: str,
                 starts_at: datetime, ends_at: datetime) -> PartyTuple:
    """Create a party."""
    party = Party(party_id, brand_id, title, starts_at, ends_at)

    db.session.add(party)
    db.session.commit()

    return party.to_tuple()


def update_party(party_id: PartyID, title: str, starts_at: datetime,
                 ends_at: datetime, is_archived: bool) -> PartyTuple:
    """Update a party."""
    party = find_party(party_id)

    if party is None:
        raise UnknownPartyId(party_id)

    party.title = title
    party.starts_at = starts_at
    party.ends_at = ends_at
    party.is_archived = is_archived

    db.session.commit()

    return party.to_tuple()


def count_parties() -> int:
    """Return the number of parties (of all brands)."""
    return Party.query.count()


def count_parties_for_brand(brand_id: BrandID) -> int:
    """Return the number of parties for that brand."""
    return Party.query \
        .filter_by(brand_id=brand_id) \
        .count()


def find_party(party_id: PartyID) -> Optional[Party]:
    """Return the party with that id, or `None` if not found."""
    return Party.query.get(party_id)


def get_all_parties_with_brands() -> List[Party]:
    """Return all parties."""
    return Party.query \
        .options(db.joinedload('brand')) \
        .all()


def get_active_parties() -> List[PartyTuple]:
    """Return active (i.e. non-archived) parties."""
    parties = Party.query \
        .filter_by(is_archived=False) \
        .order_by(Party.starts_at.desc()) \
        .all()

    return [party.to_tuple() for party in parties]


def get_archived_parties_for_brand(brand_id: BrandID) -> List[PartyTuple]:
    """Return archived parties for that brand."""
    parties = Party.query \
        .filter_by(brand_id=brand_id) \
        .filter_by(is_archived=True) \
        .order_by(Party.starts_at.desc()) \
        .all()

    return [party.to_tuple() for party in parties]


def get_parties(party_ids: Set[PartyID]) -> List[PartyTuple]:
    """Return the parties with those IDs."""
    if not party_ids:
        return []

    parties = Party.query \
        .filter(Party.id.in_(party_ids)) \
        .all()

    return [party.to_tuple() for party in parties]


def get_parties_for_brand_paginated(brand_id: BrandID, page: int,
                                    per_page: int) -> Pagination:
    """Return the parties for that brand to show on the specified page."""
    return Party.query \
        .filter_by(brand_id=brand_id) \
        .order_by(Party.starts_at.desc()) \
        .paginate(page, per_page)


def get_party_count_by_brand_id() -> Dict[BrandID, int]:
    """Return party count (including 0) per brand, indexed by brand ID."""
    return dict(db.session \
        .query(
            Brand.id,
            db.func.count(Party.id)
        ) \
        .outerjoin(Party) \
        .group_by(Brand.id) \
        .all())
