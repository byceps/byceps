"""
byceps.blueprints.admin.ticketing.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from wtforms import StringField
from wtforms.validators import InputRequired, ValidationError

from ....services.ticketing import ticket_code_service
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


class UpdateCodeForm(LocalizedForm):
    code = StringField('Code', [InputRequired()])

    @staticmethod
    def validate_code(form, field):
        if not ticket_code_service.is_ticket_code_wellformed(field.data):
            raise ValueError('Ungültiges Format')


class SpecifyUserForm(LocalizedForm):
    user = StringField('Benutzername', [InputRequired(), validate_user])
