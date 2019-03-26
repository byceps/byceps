"""
byceps.services.terms.version_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db
from ...typing import BrandID

from ..consent.transfer.models import SubjectID as ConsentSubjectID
from ..snippet.transfer.models import SnippetVersionID

from .models.version import CurrentVersionAssociation, Version
from .transfer.models import VersionID


def create_version(brand_id: BrandID, title: str,
                   snippet_version_id: SnippetVersionID,
                   consent_subject_id: ConsentSubjectID
                  ) -> Version:
    """Create a new version of the terms for that brand."""
    version = Version(brand_id, title, snippet_version_id, consent_subject_id)

    db.session.add(version)
    db.session.commit()

    return version


def find_version(version_id: VersionID) -> Optional[Version]:
    """Return the version with that id, or `None` if not found."""
    return Version.query.get(version_id)


def find_current_version_id(brand_id: BrandID) -> Optional[VersionID]:
    """Return the ID of the current version of the terms for that brand,
    or `None` if no current version is defined.
    """
    return db.session \
        .query(CurrentVersionAssociation.version_id) \
        .filter(CurrentVersionAssociation.brand_id == brand_id) \
        .scalar()


def find_current_version(brand_id: BrandID) -> Optional[Version]:
    """Return the current version of the terms for that brand, or `None`
    if none is defined.
    """
    return Version.query \
        .join(CurrentVersionAssociation) \
        .filter(CurrentVersionAssociation.brand_id == brand_id) \
        .one_or_none()


def get_current_version(brand_id: BrandID) -> Version:
    """Return the current version of the terms for that brand, or raise
    an exception if none is defined.
    """
    current_version = find_current_version(brand_id)

    if current_version is None:
        raise NoCurrentTermsVersionSpecifiedForBrand(brand_id)

    return current_version


class NoCurrentTermsVersionSpecifiedForBrand(Exception):

    def __init__(self, brand_id: BrandID) -> None:
        self.brand_id = brand_id


def set_current_version(brand_id: BrandID, version_id: VersionID) -> None:
    """Set the current version of the terms for that brand."""
    CurrentVersionAssociation.query \
        .filter_by(brand_id=brand_id) \
        .update({CurrentVersionAssociation.version_id: str(version_id)})
    db.session.commit()


def get_versions_for_brand(brand_id: BrandID) -> Sequence[Version]:
    """Return all versions for that brand, ordered by creation date."""
    return Version.query \
        .for_brand(brand_id) \
        .options(
            db.joinedload('snippet_version')
        ) \
        .latest_first() \
        .all()
