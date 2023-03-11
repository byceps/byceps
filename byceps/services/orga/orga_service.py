"""
byceps.services.orga.orga_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional, Sequence

from sqlalchemy import delete, select

from ...database import db
from ...typing import BrandID, UserID

from ..brand.dbmodels.brand import DbBrand
from ..user import user_log_service
from ..user.dbmodels.user import DbUser

from .dbmodels import DbOrgaFlag


def get_person_count_by_brand_id() -> dict[BrandID, int]:
    """Return organizer count (including 0) per brand, indexed by brand ID."""
    brand_ids_and_orga_flag_counts = (
        db.session.execute(
            select(DbBrand.id, db.func.count(DbOrgaFlag.brand_id))
            .outerjoin(DbOrgaFlag)
            .group_by(DbBrand.id)
        )
        .tuples()
        .all()
    )

    return dict(brand_ids_and_orga_flag_counts)


def get_orgas_for_brand(brand_id: BrandID) -> Sequence[DbUser]:
    """Return all users flagged as organizers for the brand."""
    return (
        db.session.scalars(
            select(DbUser)
            .join(DbOrgaFlag)
            .filter(DbOrgaFlag.brand_id == brand_id)
            .options(db.joinedload(DbUser.detail))
        )
        .unique()
        .all()
    )


def count_orgas_for_brand(brand_id: BrandID) -> int:
    """Return the number of organizers with the organizer flag set for
    that brand.
    """
    return db.session.scalar(
        select(db.func.count(DbUser.id))
        .distinct(DbUser.id)
        .join(DbOrgaFlag)
        .filter(DbOrgaFlag.brand_id == brand_id)
    )


def add_orga_flag(
    brand_id: BrandID, user_id: UserID, initiator_id: UserID
) -> DbOrgaFlag:
    """Add an orga flag for a user for that brand."""
    orga_flag = DbOrgaFlag(brand_id, user_id)
    db.session.add(orga_flag)

    log_entry = user_log_service.build_entry(
        'orgaflag-added',
        user_id,
        {
            'brand_id': str(brand_id),
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(log_entry)

    db.session.commit()

    return orga_flag


def remove_orga_flag(
    brand_id: BrandID, user_id: UserID, initiator_id: UserID
) -> None:
    """Remove the orga flag."""
    db.session.execute(
        delete(DbOrgaFlag)
        .filter_by(brand_id=brand_id)
        .filter_by(user_id=user_id)
    )

    log_entry = user_log_service.build_entry(
        'orgaflag-removed',
        user_id,
        {
            'brand_id': str(brand_id),
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(log_entry)

    db.session.commit()


def find_orga_flag(brand_id: BrandID, user_id: UserID) -> Optional[DbOrgaFlag]:
    """Return the orga flag for that brand and user, or `None` if not found."""
    return db.session.scalars(
        select(DbOrgaFlag)
        .filter_by(brand_id=brand_id)
        .filter_by(user_id=user_id)
    ).first()
