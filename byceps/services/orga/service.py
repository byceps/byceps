"""
byceps.services.orga.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict, Iterator, Optional, Sequence, Tuple

from ...database import db
from ...typing import BrandID, UserID

from ..brand.models.brand import Brand
from ..user import event_service as user_event_service
from ..user.models.user import User as DbUser

from .models import OrgaFlag


def get_brands_with_person_counts() -> Iterator[Tuple[Brand, int]]:
    """Yield (brand, person count) pairs."""
    brands = Brand.query.all()

    person_counts_by_brand_id = get_person_count_by_brand_id()

    for brand in brands:
        person_count = person_counts_by_brand_id[brand.id]
        yield brand, person_count


def get_person_count_by_brand_id() -> Dict[BrandID, int]:
    """Return organizer count (including 0) per brand, indexed by brand ID."""
    brand_ids_and_orga_flag_counts = db.session \
        .query(
            Brand.id,
            db.func.count(OrgaFlag.brand_id)
        ) \
        .outerjoin(OrgaFlag) \
        .group_by(Brand.id) \
        .all()

    return dict(brand_ids_and_orga_flag_counts)


def get_orgas_for_brand(brand_id: BrandID) -> Sequence[DbUser]:
    """Return all users flagged as organizers for the brand."""
    return DbUser.query \
        .join(OrgaFlag).filter(OrgaFlag.brand_id == brand_id) \
        .options(db.joinedload('detail')) \
        .all()


def count_orgas() -> int:
    """Return the number of organizers with the organizer flag set."""
    return DbUser.query \
        .distinct(DbUser.id) \
        .join(OrgaFlag) \
        .count()


def count_orgas_for_brand(brand_id: BrandID) -> int:
    """Return the number of organizers with the organizer flag set for
    that brand.
    """
    return DbUser.query \
        .distinct(DbUser.id) \
        .join(OrgaFlag).filter(OrgaFlag.brand_id == brand_id) \
        .count()


def add_orga_flag(
    brand_id: BrandID, user_id: UserID, initiator_id: UserID
) -> OrgaFlag:
    """Add an orga flag for a user for that brand."""
    orga_flag = OrgaFlag(brand_id, user_id)
    db.session.add(orga_flag)

    event = user_event_service.build_event('orgaflag-added', user_id, {
        'brand_id': str(brand_id),
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()

    return orga_flag


def remove_orga_flag(orga_flag: OrgaFlag, initiator_id: UserID) -> None:
    """Remove the orga flag."""
    db.session.delete(orga_flag)

    user_id = orga_flag.user_id
    event = user_event_service.build_event('orgaflag-removed', user_id, {
        'brand_id': str(orga_flag.brand_id),
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()


def find_orga_flag(brand_id: BrandID, user_id: UserID) -> Optional[OrgaFlag]:
    """Return the orga flag for that brand and user, or `None` if not found."""
    return OrgaFlag.query \
        .filter_by(brand_id=brand_id) \
        .filter_by(user_id=user_id) \
        .first()


def is_user_orga(user_id: UserID) -> bool:
    """Return `True` if the user is an organizer."""
    return db.session \
        .query(
            db.session \
                .query(OrgaFlag) \
                .filter_by(user_id=user_id) \
                .exists()
        ) \
        .scalar()
