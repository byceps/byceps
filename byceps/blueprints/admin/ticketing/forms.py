"""
byceps.blueprints.admin.ticketing.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import StringField
from wtforms.validators import InputRequired, ValidationError

from ....services.user import service as user_service
from ....util.l10n import LocalizedForm


def validate_user(form, field):
    screen_name = field.data.strip()

    user = user_service.find_user_by_screen_name(
        screen_name, case_insensitive=True
    )

    if user is None:
        raise ValidationError('Unbekannter Benutzername')

    field.data = user.to_dto()


class SpecifyUserForm(LocalizedForm):
    user = StringField('Benutzername', [InputRequired(), validate_user])
