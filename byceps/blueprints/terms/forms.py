"""
byceps.blueprints.terms.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import BooleanField
from wtforms.validators import InputRequired

from ...util.l10n import LocalizedForm


class ConsentForm(LocalizedForm):
    consent_to_terms = BooleanField('AGB', [InputRequired()])
