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


def get_party_counts_by_brand_id():
    """Return party counts (including 0) per brand, indexed by brand ID."""
    return dict(db.session \
        .query(
            Brand.id,
            db.func.count(Party.id)
        ) \
        .outerjoin(Party) \
        .group_by(Brand.id) \
        .all())
