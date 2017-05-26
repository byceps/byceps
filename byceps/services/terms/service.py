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

from .models import Consent, ConsentContext, Version, VersionID


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


def get_current_version(brand_id: BrandID) -> Optional[Version]:
    """Return the current version of the terms for that brand, or `None`
    if none is defined.
    """
    return Version.query \
        .for_brand_id(brand_id) \
        .latest_first() \
        .first()


def get_versions_for_brand(brand_id: BrandID) -> Sequence[Version]:
    """Return all versions for that brand, ordered by creation date."""
    return Version.query \
        .for_brand_id(brand_id) \
        .order_by(Version.created_at.desc()) \
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
