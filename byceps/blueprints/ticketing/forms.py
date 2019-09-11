"""
byceps.blueprints.ticketing.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g

from wtforms import StringField
from wtforms.validators import InputRequired, ValidationError

from ...services.consent import consent_service
from ...services.terms import version_service as terms_version_service
from ...services.user import service as user_service
from ...util.l10n import LocalizedForm


def validate_user(form, field):
    screen_name = field.data.strip()

    user = user_service.find_user_by_screen_name(screen_name)

    if user is None:
        raise ValidationError('Unbekannter Benutzername')

    user = user.to_dto()

    terms_version = terms_version_service \
        .find_current_version_for_brand(g.brand_id)

    if terms_version and not consent_service.has_user_consented_to_subject(
                user.id, terms_version.consent_subject_id):
        raise ValidationError(
            'Der Benutzer "{}" hat die aktuellen AGB der {} noch nicht akzeptiert.'
                .format(user.screen_name, terms_version.brand.title))

    field.data = user


class SpecifyUserForm(LocalizedForm):
    user = StringField('Benutzername', [InputRequired(), validate_user])
