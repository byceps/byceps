"""
byceps.blueprints.terms.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import BooleanField, HiddenField
from wtforms.validators import InputRequired

from ...util.l10n import LocalizedForm


def create_consent_form(subject_ids):
    subject_ids_str = ','.join(subject_id.hex for subject_id in subject_ids)

    class ConsentForm(LocalizedForm):
        subject_ids = HiddenField(None, [InputRequired()],
                                  default=subject_ids_str)

    for subject_id in subject_ids:
        field_name = 'subject_{}'.format(subject_id.hex)
        field = BooleanField(None, [InputRequired()])
        setattr(ConsentForm, field_name, field)

    return ConsentForm
