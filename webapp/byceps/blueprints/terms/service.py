# -*- coding: utf-8 -*-

"""
byceps.blueprints.terms.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from .models import Consent, ConsentContext, Version


def get_current_version(brand):
    """Return the current version of the terms for that brand."""
    return Version.query.for_brand(brand).latest_first().first()


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


def has_user_accepted_version(user, version):
    """Tell if the user has accepted the specified version of the terms."""
    count = Consent.query \
        .filter_by(user=user) \
        .filter_by(version=version) \
        .count()
    return count > 0
