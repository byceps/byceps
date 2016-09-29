# -*- coding: utf-8 -*-

"""
byceps.services.terms.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models import Consent, ConsentContext, Version


def find_version(version_id):
    """Return the version with that id, or `None` if not found."""
    return Version.query.get(version_id)


def get_current_version(brand_id):
    """Return the current version of the terms for that brand."""
    return Version.query \
        .for_brand_id(brand_id) \
        .latest_first() \
        .first()


def get_versions_for_brand(brand_id):
    """Return all versions for that brand, ordered by creation date."""
    return Version.query \
        .for_brand_id(brand_id) \
        .order_by(Version.created_at.desc()) \
        .all()


def build_consent_on_account_creation(user_id, version_id):
    """Create user's consent to that version expressed on account creation."""
    context = ConsentContext.account_creation
    return Consent(user_id, version_id, context)


def build_consent_on_separate_action(user_id, version_id):
    """Create user's consent to that version expressed through a
    separate action.
    """
    context = ConsentContext.separate_action
    return Consent(user_id, version_id, context)


def consent_to_version_on_separate_action(version_id, verification_token):
    """Store the user's consent to that version, and invalidate the
    verification token.
    """
    user_id = verification_token.user_id
    db.session.delete(verification_token)

    consent = build_consent_on_separate_action(user_id, version_id)
    db.session.add(consent)

    db.session.commit()


def has_user_accepted_version(user_id, version_id):
    """Tell if the user has accepted the specified version of the terms."""
    count = Consent.query \
        .filter_by(user_id=user_id) \
        .filter_by(version_id=version_id) \
        .count()
    return count > 0
