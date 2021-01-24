"""
byceps.blueprints.site.user.settings.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import g
from flask_babel import lazy_gettext
from wtforms import PasswordField, StringField
from wtforms.fields.html5 import DateField, TelField
from wtforms.validators import InputRequired, Length, Optional

from .....services.authentication.password import service as password_service
from .....services.user import screen_name_validator, service as user_service
from .....util.l10n import LocalizedForm

from ....common.core.forms import ScreenNameValidator


class ChangeScreenNameForm(LocalizedForm):
    screen_name = StringField(
        lazy_gettext('Neuer Benutzername'),
        [
            InputRequired(),
            Length(
                min=screen_name_validator.MIN_LENGTH,
                max=screen_name_validator.MAX_LENGTH,
            ),
            ScreenNameValidator(),
        ],
    )
    password = PasswordField(
        lazy_gettext('Aktuelles Passwort'), [InputRequired()]
    )

    @staticmethod
    def validate_screen_name(form, field):
        if g.user.screen_name == field.data:
            raise ValueError(
                lazy_gettext('Dies ist bereits der aktuelle Benutzername.')
            )

        if user_service.is_screen_name_already_assigned(field.data):
            raise ValueError(
                lazy_gettext('Dieser Benutzername kann nicht verwendet werden.')
            )

    @staticmethod
    def validate_password(form, field):
        user_id = g.user.id
        password = field.data

        if not password_service.is_password_valid_for_user(user_id, password):
            raise ValueError(lazy_gettext('Das Passwort ist nicht korrekt.'))


class DetailsForm(LocalizedForm):
    first_names = StringField(
        lazy_gettext('Vorname(n)'), [InputRequired(), Length(min=2)]
    )
    last_name = StringField(
        lazy_gettext('Nachname'), [InputRequired(), Length(min=2, max=80)]
    )
    date_of_birth = DateField(lazy_gettext('Geburtsdatum'), [Optional()])
    country = StringField(lazy_gettext('Land'), [Optional(), Length(max=60)])
    zip_code = StringField(lazy_gettext('PLZ'), [Optional()])
    city = StringField(lazy_gettext('Stadt'), [Optional()])
    street = StringField(lazy_gettext('Straße'), [Optional()])
    phone_number = TelField(
        lazy_gettext('Telefonnummer'), [Optional(), Length(max=20)]
    )
