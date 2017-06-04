"""
byceps.services.terms.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db
from ...typing import BrandID, UserID

from ..verification_token.models import Token

from .models import Consent, ConsentContext, CurrentVersionAssociation, \
    Version, VersionID


# -------------------------------------------------------------------- #
# version


def create_version(brand_id: BrandID, creator_id: UserID, title: str, body: str
                  ) -> Version:
    """Create a new version of the terms for that brand."""
    version = Version(brand_id, creator_id, title, body)

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


def get_versions_for_brand(brand_id: BrandID) -> Sequence[Version]:
    """Return all versions for that brand, ordered by creation date."""
    return Version.query \
        .for_brand_id(brand_id) \
        .latest_first() \
        .all()


# -------------------------------------------------------------------- #
# consent


def build_consent_on_account_creation(user_id: UserID, version_id: VersionID) \
                                      -> Consent:
    """Create user's consent to that version expressed on account creation."""
    context = ConsentContext.account_creation
    return Consent(user_id, version_id, context)


def build_consent_on_separate_action(user_id: UserID, version_id: VersionID) \
                                     -> Consent:
    """Create user's consent to that version expressed through a
    separate action.
    """
    context = ConsentContext.separate_action
    return Consent(user_id, version_id, context)


def consent_to_version_on_separate_action(version_id: VersionID,
                                          verification_token: Token) -> None:
    """Store the user's consent to that version, and invalidate the
    verification token.
    """
    user_id = verification_token.user_id
    db.session.delete(verification_token)

    consent = build_consent_on_separate_action(user_id, version_id)
    db.session.add(consent)

    db.session.commit()


def get_consents_by_user(user_id: UserID) -> Sequence[Consent]:
    """Return the consents the user submitted."""
    return Consent.query \
        .filter_by(user_id=user_id) \
        .all()


def has_user_accepted_version(user_id: UserID, version_id: VersionID) -> bool:
    """Tell if the user has accepted the specified version of the terms."""
    count = Consent.query \
        .filter_by(user_id=user_id) \
        .filter_by(version_id=version_id) \
        .count()
    return count > 0
