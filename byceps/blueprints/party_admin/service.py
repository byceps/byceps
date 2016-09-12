# -*- coding: utf-8 -*-

"""
byceps.blueprints.party_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..brand.models import Brand
from ..party.models import Party


def get_parties_with_brands():
    """Return all parties."""
    return Party.query \
        .options(db.joinedload('brand')) \
        .all()


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


def create_party(party_id, brand_id, title, starts_at, ends_at):
    """Create a party."""
    party = Party(party_id, brand_id, title, starts_at, ends_at)

    db.session.add(party)
    db.session.commit()

    return party
