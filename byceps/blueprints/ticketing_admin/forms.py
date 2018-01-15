"""
byceps.blueprints.ticketing_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import StringField
from wtforms.validators import InputRequired, ValidationError

from ...services.user import service as user_service
from ...util.l10n import LocalizedForm


def validate_user(form, field):
    screen_name = field.data.strip()

    user = user_service.find_user_by_screen_name(screen_name)

    if user is None:
        raise ValidationError('Unbekannter Benutzername')

    field.data = user


class SpecifyUserForm(LocalizedForm):
    user = StringField('Benutzername', [InputRequired(), validate_user])
