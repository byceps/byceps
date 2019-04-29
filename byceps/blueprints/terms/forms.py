"""
byceps.blueprints.terms.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import BooleanField, HiddenField
from wtforms.validators import InputRequired

from ...util.l10n import LocalizedForm


class ConsentForm(LocalizedForm):
    terms_consent_subject_id = HiddenField(None, [InputRequired()])
    consent_to_terms = BooleanField('AGB', [InputRequired()])
