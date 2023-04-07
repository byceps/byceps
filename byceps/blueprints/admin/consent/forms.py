"""
byceps.blueprints.admin.consent.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext
from wtforms import SelectField, StringField
from wtforms.validators import InputRequired, Length, ValidationError

from ....services.consent import consent_subject_service
from ....typing import BrandID
from ....util.l10n import LocalizedForm


class SubjectCreateForm(LocalizedForm):
    subject_name = StringField(
        lazy_gettext('Internal name'), [InputRequired(), Length(max=40)]
    )
    subject_title = StringField(
        lazy_gettext('Internal title'), [InputRequired(), Length(max=40)]
    )
    checkbox_label = StringField(
        lazy_gettext('Checkbox label'), [InputRequired(), Length(max=200)]
    )
    checkbox_link_target = StringField(
        lazy_gettext('Checkbox label link target'),
        [InputRequired(), Length(max=200)],
    )


class RequirementCreateForm(LocalizedForm):
    subject_id = SelectField(lazy_gettext('Consent subject'), [InputRequired()])

    def set_subject_id_choices(self, brand_id: BrandID):
        all_subjects = consent_subject_service.get_all_subjects()

        subject_ids_required_for_brand = (
            consent_subject_service.get_subject_ids_required_for_brand(brand_id)
        )

        selectable_subjects = {
            subject
            for subject in all_subjects
            if subject.id not in subject_ids_required_for_brand
        }

        choices = [
            (subject.id, subject.name) for subject in selectable_subjects
        ]
        choices.sort(key=lambda choice: choice[1])

        self.subject_id.choices = choices

    @staticmethod
    def validate_subject_id(form, field):
        subject_id = field.data
        subject = consent_subject_service.find_subject(subject_id)
        if subject is None:
            raise ValidationError(lazy_gettext('Invalid choice'))
