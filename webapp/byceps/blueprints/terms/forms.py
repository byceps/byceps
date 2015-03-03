# -*- coding: utf-8 -*-

"""
byceps.blueprints.terms.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from wtforms import BooleanField
from wtforms.validators import DataRequired

from ...util.l10n import LocalizedForm


class ConsentForm(LocalizedForm):
    consent_to_terms = BooleanField('AGB', [DataRequired()])
