"""
byceps.blueprints.ticketing.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g

from wtforms import StringField
from wtforms.validators import InputRequired, ValidationError

from ...services.terms import service as terms_service
from ...services.user import service as user_service
from ...util.l10n import LocalizedForm


def validate_user(form, field):
    screen_name = field.data.strip()

    user = user_service.find_user_by_screen_name(screen_name)

    if user is None:
        raise ValidationError('Unbekannter Benutzername')

    terms_version = terms_service.get_current_version(g.brand_id)

    if not terms_service.has_user_accepted_version(user.id, terms_version.id):
        raise ValidationError(
            'Der Benutzer "{}" hat die aktuellen AGB der {} noch nicht akzeptiert.'
                .format(user.screen_name, terms_version.brand.title))

    field.data = user


class SpecifyUserForm(LocalizedForm):
    user = StringField('Benutzername', [InputRequired(), validate_user])
