# -*- coding: utf-8 -*-

"""
byceps.blueprints.terms.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models import Consent, ConsentContext, Version


def find_version(version_id):
    """Return the version with that id, or `None` if not found."""
    return Version.query.get(version_id)


def get_current_version(brand):
    """Return the current version of the terms for that brand."""
    return Version.query.for_brand(brand).latest_first().first()


def get_versions_for_brand(brand):
    """Return all versions for that brand, ordered by creation date."""
    return Version.query \
        .for_brand(brand) \
        .order_by(Version.created_at.desc()) \
        .all()


def build_consent_on_account_creation(user, version):
    """Create user's consent to that version expressed on account creation."""
    context = ConsentContext.account_creation
    return Consent(user, version, context)


def build_consent_on_separate_action(user, version):
    """Create user's consent to that version expressed through a
    separate action.
    """
    context = ConsentContext.separate_action
    return Consent(user, version, context)


def consent_to_version_on_separate_action(version, verification_token):
    """Store the user's consent to that version, and invalidate the
    verification token.
    """
    user = verification_token.user
    db.session.delete(verification_token)

    consent = build_consent_on_separate_action(user, version)
    db.session.add(consent)

    db.session.commit()


def has_user_accepted_version(user, version):
    """Tell if the user has accepted the specified version of the terms."""
    count = Consent.query \
        .filter_by(user=user) \
        .filter_by(version=version) \
        .count()
    return count > 0
