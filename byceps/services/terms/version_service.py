"""
byceps.services.terms.version_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence
from uuid import UUID

from ...database import db
from ...typing import BrandID

from ..brand import settings_service as brand_settings_service
from ..consent.transfer.models import SubjectID as ConsentSubjectID
from ..snippet.transfer.models import SnippetVersionID

from .models.version import Version
from .transfer.models import DocumentID, VersionID


BRAND_SETTING_KEY_CURRENT_VERSION_ID = 'terms_current_version_id'


def create_version(brand_id: BrandID, document_id: DocumentID, title: str,
                   snippet_version_id: SnippetVersionID,
                   consent_subject_id: ConsentSubjectID
                  ) -> Version:
    """Create a new version of the terms for that brand."""
    version = Version(brand_id, document_id, title, snippet_version_id,
                      consent_subject_id)

    db.session.add(version)
    db.session.commit()

    return version


def find_version(version_id: VersionID) -> Optional[Version]:
    """Return the version with that ID, or `None` if not found."""
    return Version.query.get(version_id)


def find_version_for_consent_subject_id(consent_subject_id: ConsentSubjectID
                                       ) -> Optional[Version]:
    """Return the version with that consent subject ID, or `None` if
    not found.
    """
    return Version.query \
        .filter_by(consent_subject_id=consent_subject_id) \
        .one_or_none()


def find_current_version_id(brand_id: BrandID) -> Optional[VersionID]:
    """Return the ID of the current version of the terms for that brand,
    or `None` if no current version is defined.
    """
    value = brand_settings_service \
        .find_setting_value(brand_id, BRAND_SETTING_KEY_CURRENT_VERSION_ID)

    if value is None:
        return None

    return VersionID(UUID(value))


def find_current_version(brand_id: BrandID) -> Optional[Version]:
    """Return the current version of the terms for that brand, or `None`
    if none is defined.
    """
    current_version_id = find_current_version_id(brand_id)

    if current_version_id is None:
        return None

    return find_version(current_version_id)


def set_current_version(brand_id: BrandID, version_id: VersionID) -> None:
    """Set the current version of the terms for that brand."""
    brand_settings_service.create_or_update_setting(
        brand_id, BRAND_SETTING_KEY_CURRENT_VERSION_ID, str(version_id))


def get_versions_for_brand(brand_id: BrandID) -> Sequence[Version]:
    """Return all versions for that brand, ordered by creation date."""
    return Version.query \
        .for_brand(brand_id) \
        .options(
            db.joinedload('snippet_version')
        ) \
        .latest_first() \
        .all()
