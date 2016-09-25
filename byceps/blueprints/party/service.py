# -*- coding: utf-8 -*-

"""
byceps.blueprints.party.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..brand.models import Brand

from .models import Party


def count_parties():
    """Return the number of parties (of all brands)."""
    return Party.query.count()


def count_parties_for_brand(brand_id):
    """Return the number of parties for that brand."""
    return Party.query \
        .for_brand_id(brand_id) \
        .count()


def get_party_count_by_brand_id():
    """Return party count (including 0) per brand, indexed by brand ID."""
    return dict(db.session \
        .query(
            Brand.id,
            db.func.count(Party.id)
        ) \
        .outerjoin(Party) \
        .group_by(Brand.id) \
        .all())


def get_parties_for_brand_paginated(brand_id, page, per_page):
    """Return the parties for that brand to show on the specified page."""
    return Party.query \
        .for_brand_id(brand_id) \
        .paginate(page, per_page)


def find_party(party_id):
    """Return the party with that id, or `None` if not found."""
    return Party.query.get(party_id)


def find_party_with_brand(party_id):
    """Return the party with that id, or `None` if not found."""
    return Party.query \
        .options(db.joinedload('brand')) \
        .get(party_id)


def get_all_parties_with_brands():
    """Return all parties."""
    return Party.query \
        .options(db.joinedload('brand')) \
        .all()


def get_archived_parties():
    """Return archived parties."""
    return Party.query \
        .filter_by(is_archived=True) \
        .order_by(Party.starts_at.desc()) \
        .all()


def get_parties(party_ids):
    """Return the parties with those IDs."""
    if not party_ids:
        return []

    return Party.query \
        .filter(Party.id.in_(party_ids)) \
        .all()


def create_party(party_id, brand_id, title, starts_at, ends_at):
    """Create a party."""
    party = Party(party_id, brand_id, title, starts_at, ends_at)

    db.session.add(party)
    db.session.commit()

    return party
