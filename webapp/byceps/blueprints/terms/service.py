# -*- coding: utf-8 -*-

"""
byceps.blueprints.terms.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from .models import Consent, ConsentContext, Version


def get_current_version():
    """Return the current version of the terms for the current brand."""
    return Version.query.for_current_brand().latest_first().first()


def build_consent_on_account_creation(user, version):
    """Create user's consent to that version expressed on account creation."""
    context = ConsentContext.account_creation
    return Consent(user, version, context)
