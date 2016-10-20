# -*- coding: utf-8 -*-

"""
byceps.services.orga.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from itertools import islice

from ...database import db

from ..brand.models import Brand
from ..user.models.detail import UserDetail
from ..user.models.user import User

from .models import OrgaFlag


def get_brands_with_person_counts():
    """Yield (brand, person count) pairs."""
    brands = Brand.query.all()

    person_counts_by_brand_id = get_person_count_by_brand_id()

    for brand in brands:
        person_count = person_counts_by_brand_id[brand.id]
        yield brand, person_count


def get_person_count_by_brand_id():
    """Return organizer count (including 0) per brand, indexed by brand ID."""
    return dict(db.session \
        .query(
            Brand.id,
            db.func.count(OrgaFlag.brand_id)
        ) \
        .outerjoin(OrgaFlag) \
        .group_by(Brand.id) \
        .all())


def get_orgas_for_brand(brand_id):
    """Return all users flagged as organizers for the brand."""
    return User.query \
        .join(OrgaFlag).filter(OrgaFlag.brand_id == brand_id) \
        .options(db.joinedload('detail')) \
        .all()


def collect_orgas_with_next_birthdays(*, limit=None):
    """Yield the next birthdays of organizers, sorted by month and day."""
    orgas_with_birthdays = collect_orgas_with_birthdays()

    sorted_orgas = sort_users_by_next_birthday(orgas_with_birthdays)

    if limit is not None:
        sorted_orgas = islice(sorted_orgas, limit)

    yield from sorted_orgas


def collect_orgas_with_birthdays():
    """Return all organizers whose birthday is known."""
    return User.query \
        .join(OrgaFlag) \
        .join(UserDetail) \
        .filter(UserDetail.date_of_birth != None) \
        .options(db.joinedload('detail')) \
        .all()


def sort_users_by_next_birthday(users):
    return sorted(users,
                  key=lambda user: (
                    user.detail.days_until_next_birthday,
                    -user.detail.age))


def count_orgas():
    """Return the number of organizers with the organizer flag set."""
    return User.query \
        .join(OrgaFlag) \
        .count()


def count_orgas_for_brand(brand_id):
    """Return the number of organizers with the organizer flag set for
    that brand.
    """
    return User.query \
        .join(OrgaFlag).filter(OrgaFlag.brand_id == brand_id) \
        .count()


def create_orga_flag(brand_id, user_id):
    """Create an orga flag for a user for brand."""
    orga_flag = OrgaFlag(brand_id, user_id)

    db.session.add(orga_flag)
    db.session.commit()

    return orga_flag


def delete_orga_flag(orga_flag):
    """Delete the orga flag."""
    db.session.delete(orga_flag)
    db.session.commit()


def find_orga_flag(brand_id, user_id):
    """Return the orga flag for that brand and user, or `None` if not found."""
    return OrgaFlag.query \
        .filter_by(brand_id=brand_id) \
        .filter_by(user_id=user_id) \
        .first()


def is_user_orga(user_id):
    """Return `True` if the user is an organizer."""
    flag_count = OrgaFlag.query \
        .filter_by(user_id=user_id) \
        .count()

    return flag_count > 0
