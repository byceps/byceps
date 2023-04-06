"""
byceps.services.consent.brand_requirements_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import delete

from ...database import db
from ...typing import BrandID

from .dbmodels import DbBrandRequirement
from .models import SubjectID


def create_brand_requirement(brand_id: BrandID, subject_id: SubjectID) -> None:
    """Create a brand requirement."""
    db_brand_requirement = DbBrandRequirement(brand_id, subject_id)

    db.session.add(db_brand_requirement)
    db.session.commit()


def delete_brand_requirement(brand_id: BrandID, subject_id: SubjectID) -> None:
    """Delete a brand requirement."""
    db.session.execute(
        delete(DbBrandRequirement)
        .filter_by(brand_id=brand_id)
        .filter_by(subject_id=subject_id)
    )
    db.session.commit()
