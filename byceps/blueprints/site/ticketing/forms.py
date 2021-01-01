"""
byceps.blueprints.site.ticketing.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import g

from wtforms import StringField
from wtforms.validators import InputRequired, ValidationError

from ....services.consent import (
    consent_service,
    subject_service as consent_subject_service,
)
from ....services.user import service as user_service
from ....util.l10n import LocalizedForm


def validate_user(form, field):
    screen_name = field.data.strip()

    user = user_service.find_user_by_screen_name(
        screen_name, case_insensitive=True
    )

    if user is None:
        raise ValidationError('Unbekannter Benutzername')

    user = user.to_dto()

    required_consent_subjects = (
        consent_subject_service.get_subjects_required_for_brand(g.brand_id)
    )
    required_consent_subject_ids = {
        subject.id for subject in required_consent_subjects
    }

    if not consent_service.has_user_consented_to_all_subjects(
        user.id, required_consent_subject_ids
    ):
        raise ValidationError(
            f'Benutzer "{user.screen_name}" hat noch nicht alle nötigen '
            'Zustimmungen erteilt. Ein erneuter Login ist erforderlich.'
        )

    field.data = user


class SpecifyUserForm(LocalizedForm):
    user = StringField('Benutzername', [InputRequired(), validate_user])
