"""
byceps.blueprints.site.consent.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import BooleanField, HiddenField
from wtforms.validators import InputRequired

from ....util.l10n import LocalizedForm


def create_consent_form(subjects):
    subject_ids_str = ','.join(subject.id.hex for subject in subjects)

    class ConsentForm(LocalizedForm):
        subject_ids = HiddenField(
            None, [InputRequired()], default=subject_ids_str
        )

    for subject in subjects:
        field_name = get_subject_field_name(subject)
        field = BooleanField(None, [InputRequired()])
        setattr(ConsentForm, field_name, field)

    return ConsentForm


def get_subject_field_name(subject):
    return f'subject_{subject.id.hex}'
